import datetime
from django.utils import timezone
from django.db import models
from django.forms import ValidationError
from cotizador.models import Receta
from django.db.models import Q
from django.contrib import messages


class Estado(models.Model):
    ESTADO=models.CharField(max_length=120,null=False,blank=False)

    def __str__(self):
        return self.ESTADO


class Cliente(models.Model):
    NUMERO_CLIENTE= models.AutoField(primary_key=True)
    NOMBRE_Y_APELLIDO=models.CharField(max_length=120,null=False,blank=False)
    EMAIL=models.CharField(max_length=120,null=True,blank=True)
    TELEFONO =models.CharField(max_length=15,null=True,blank=True)
    PEDIDOS_TOTALES = models.IntegerField(default=0,blank=True,null=True)
    PEDIDOS_ENTREGADOS = models.IntegerField(default=0,blank=True,null=True)
    PEDIDOS_PENDIENTES = models.IntegerField(default=0,blank=True,null=True)
    FECHA_PROXIMA_ENTREGA = models.DateField(blank=True,null=True)
    COMENTARIOS = models.TextField(blank=True,null=True)
                                       
    def __str__(self):
        return self.NOMBRE_Y_APELLIDO
    
    def actualizar_pedidos(self):
        pedidos_entregados = 0
        pedidos_pendientes = 0
        fecha_proxima_entrega = None

        for orden in self.orden_set.all():
            if orden.estado.ESTADO == 'Entregado':
                pedidos_entregados += 1
            elif orden.estado.ESTADO == 'Pendiente':
                pedidos_pendientes += 1
                if not fecha_proxima_entrega or orden.fecha_entrega < fecha_proxima_entrega:
                    fecha_proxima_entrega = orden.fecha_entrega

        self.PEDIDOS_TOTALES = pedidos_entregados + pedidos_pendientes
        self.PEDIDOS_ENTREGADOS = pedidos_entregados
        self.PEDIDOS_PENDIENTES = pedidos_pendientes
        self.FECHA_PROXIMA_ENTREGA = fecha_proxima_entrega

        self.save()

class Orden(models.Model):
    fecha_creacion=models.DateField(default=datetime.datetime.now,null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado,default=1,blank=True, null=True,on_delete=models.CASCADE)
    articulos = models.ManyToManyField(Receta, through='ArticuloOrden')
    total= models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    fecha_entrega = models.DateField(null=True, blank=True)
    adelanto = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, null=False)
    debe=models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    aclaraciones=models.CharField(max_length=255,null=True,blank=True)

    def clean(self):

        if self.adelanto < 0:
            raise ValidationError("El importe de adelanto no puede ser valor negativo.")


        if self.fecha_entrega and self.fecha_entrega < timezone.now().date():
            raise ValidationError("La fecha de entrega no puede ser anterior a la fecha actual.")
        
        for orden in Orden.objects.all().filter(id=self.pk):
            if orden.estado_id==6:
                raise ValidationError("No se puede modificar un pedido cancelado.") 
            elif orden.estado_id==4:
                raise ValidationError("No se puede modificar un pedido que se encuentra entregado.") 


        super().clean()

    def save(self, *args, **kwargs):

        if not self.pk:
            self.cliente.PEDIDOS_PENDIENTES += 1
            self.cliente.PEDIDOS_TOTALES += 1
            self.cliente.FECHA_PROXIMA_ENTREGA = self.fecha_entrega
            self.cliente.save()

        monto = 0

        for pago in Pago.objects.all():

            if pago.orden_asociada.pk == self.pk:
                monto += pago.pago

        self.adelanto = monto

        self.debe = self.total - self.adelanto

        super().save(*args, **kwargs)

    

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural ='Pedidos' 

    def __str__(self):
        return f"Orden #{self.id} para {self.cliente.NOMBRE_Y_APELLIDO} Pendiente: {self.debe}"

    @property
    def total(self):
        total = 0
        for articulo in self.articuloorden_set.all():
            total += articulo.subtotal
        return total

class ArticuloOrden(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    costo_receta= models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    cantidad=models.DecimalField(max_digits=20, decimal_places=2, default=1, blank=False, null=False)
    subtotal=models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    fecha_ultimo_costo=models.DateField(blank=True,null=True)
    precio=models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    ganancia=models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE)

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("Por favor ingrese una cantidad superior a 0.")
        super().clean()

    def save(self, *args, **kwargs):

        self.costo_receta = self.receta.COSTO_FINAL
        self.precio = self.receta.PRECIO_VENTA
        self.fecha_ultimo_costo = self.receta.ULTIMA_ACTUALIZACION
        self.subtotal = self.precio * self.cantidad
        print(self.precio)
        print(self.costo_receta)
        print(self.cantidad)
        print(self.fecha_ultimo_costo)
        self.ganancia = self.cantidad * (self.precio - self.costo_receta)

        super().save(*args, **kwargs)

class Pago(models.Model):
    codigo_pago = models.AutoField(primary_key=True)
    fecha=models.DateField(default=datetime.datetime.now,blank=True,null=True) 
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE,blank=False,null=False)
    orden_asociada = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        limit_choices_to=Q(debe__gt=0),
    )
    total_orden = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    pago = models.DecimalField(max_digits=20, decimal_places=2, null=False, blank=False)
    deuda_pendiente = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    fecha_vencimiento = models.DateField(default=datetime.datetime.now,null=True, blank=True)

    def clean(self):


        if self.pago <= 0:
            raise ValidationError("El pago no puede ser menor a $ 0 .-")

        Deuda = 0
        Deuda = self.orden_asociada.debe

        if self.pago > Deuda:
            raise ValidationError("El pago no puede ser superior al total restante de la orden.")

        return super().clean()

    def save(self, *args, **kwargs):

        self.total_orden = self.orden_asociada.total

        self.deuda_pendiente = self.orden_asociada.debe - self.pago
        
        super(Pago, self).save(*args, **kwargs)
        Actualizar_Pagos_Ordenes()
        self.orden_asociada.cliente.actualizar_pedidos()

    def __str__(self):

        deuda = self.total_orden - self.pago
        titulo = f"Pago N° {self.codigo_pago} - Pago total $ {self.pago} - Orden asociada N°: {self.orden_asociada.pk} - Deuda Pendiente $ {deuda}.-"
        return titulo
    
    class Meta:
        verbose_name = 'Pagos de Clientes'
        verbose_name_plural ='Pagos de Clientes' 


def Actualizar_Pagos_Ordenes():

    for pago in Orden.objects.all():

        monto = 0
        
        if pago.estado == "Entregado":
            pass
        else:
            for x in Pago.objects.all():

                if x.orden_asociada.pk == pago.pk:
                    monto += x.pago

            pago.adelanto = monto

            pago.debe = pago.total - pago.adelanto

            deuda = pago.debe

            if deuda <= 0:
                pago.estado==3

            pago.save()

class Gasto(models.Model):
    codigo_gasto = models.AutoField(primary_key=True)
    fecha=models.DateField(default=datetime.datetime.now,blank=True,null=True) 
    pago = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    detalle = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):

        titulo = f"Gasto N° {self.codigo_gasto} - Detalle: {self.detalle} - Gasto total $ {self.pago}"

        return titulo
    

class Retiro(models.Model):
    codigo_retiro = models.AutoField(primary_key=True)
    fecha=models.DateField(default=datetime.datetime.now,blank=True,null=True) 
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=False, blank=False)
    detalle = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):

        titulo = f"Retiro N° {self.codigo_retiro} - Detalle: {self.detalle} - total $ {self.total}"

        return titulo
    
class CierreCaja(models.Model):

    numero_reporte = models.AutoField(primary_key=True)
    fecha=models.DateField(default=datetime.datetime.now,blank=False,null=False,unique=True)
    efectivo_inicial = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, null=False)
    efectivo_final = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, null=False)
    total_ventas = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    gastos = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    pagos_clientes = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    retiros_efectivo = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    final = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    diferencias = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True, null=True)
    comentarios = models.TextField(blank=True,null=True)

    class Meta:
        verbose_name = 'Cierre de Caja'
        verbose_name_plural ='Cierres de Caja'

    def save(self, request=None, *args, **kwargs):

        # Obtener la fecha del día anterior
        fecha_anterior = self.fecha - datetime.timedelta(days=1)

        # Obtener el objeto de CierreCaja correspondiente a la fecha anterior
        cierre_anterior = CierreCaja.objects.filter(fecha=fecha_anterior).first()

        # Asignar el valor de efectivo_final del cierre anterior a efectivo_inicial de este cierre
        if cierre_anterior:
            self.efectivo_inicial = cierre_anterior.final
        else:
            self.efectivo_inicial = 0


        total = 0
        for venta in Orden.objects.all():
            if venta.fecha_creacion == self.fecha:
                total += venta.total
        self.total_ventas = total
        
        total = 0
        for pago in Pago.objects.all():
            if pago.fecha == self.fecha:
                total += pago.pago
        self.pagos_clientes = total

        total = 0
        for gasto in Gasto.objects.all():
            if gasto.fecha == self.fecha:
                total += gasto.pago
        self.gastos = total

        total = 0
        for retiro in Retiro.objects.all():
            if retiro.fecha == self.fecha:
                total += retiro.total
        self.retiros_efectivo = total

        self.final = self.efectivo_inicial + self.pagos_clientes - self.gastos - self.retiros_efectivo

        self.diferencias = self.efectivo_final - self.final

        super(CierreCaja, self).save(*args, **kwargs)