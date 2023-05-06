from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

UnidadDeMedida = [
    ("Unidades","Unidades"),
    ("Kilogramos","Kilogramos"),
    ("Litros","Litros"),
    ("Onzas","Onzas"),
    ("Libras","Libras"),
]

UnidadDeMedidaSalida = [
    ("Unidades","Unidades"),
    ("Gramos","Gramos"),
    ("Mililitros","Mililitros"),
    ("Onzas","Onzas"),
    ("Libras","Libras"),
]

class Insumo(models.Model):
    PRODUCTO = models.CharField(max_length=120, null=False, blank=False,unique=True)
    DETALLE = models.TextField(null=True, blank=True)
    STOCK = models.IntegerField(default=0,null=True,blank=True)
    UNIDAD_MEDIDA_COMPRA = models.CharField(max_length=10, choices=UnidadDeMedida, default="Unidades", null=False, blank=False)
    CANTIDAD = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, null=False)
    PRECIO_COMPRA = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, null=False)
    UNIDAD_MEDIDA_USO = models.CharField(max_length=10, choices=UnidadDeMedidaSalida, default="Unidades", null=False, blank=False)
    COSTO_UNITARIO = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, null=False)

    def __str__(self):
        return self.PRODUCTO

    def clean(self):

        if self.UNIDAD_MEDIDA_COMPRA == "Unidades" and self.UNIDAD_MEDIDA_USO != "Unidades":
            raise ValidationError("Si selecciona 'Unidades' en el campo Unidad de compra, solo puede utilizar 'Unidades'")
        elif self.UNIDAD_MEDIDA_COMPRA == "Kilogramos" and self.UNIDAD_MEDIDA_USO != "Kilogramos" and self.UNIDAD_MEDIDA_USO != "Gramos":
            raise ValidationError("Si selecciona 'Kilogramos' en el campo Unidad de compra, solo puede seleccionar 'Gramos'")
        elif self.UNIDAD_MEDIDA_COMPRA == "Litros" and self.UNIDAD_MEDIDA_USO != "Litros" and self.UNIDAD_MEDIDA_USO != "Mililitros":
            raise ValidationError("Si selecciona 'Litros' en el campo Unidad de compra, solo puede seleccionar 'Mililitros'")
        elif self.UNIDAD_MEDIDA_COMPRA == "Onzas" and self.UNIDAD_MEDIDA_USO != "Onzas":
            raise ValidationError("Si selecciona 'Onzas' en el campo Unidad de compra, solo puede seleccionar 'Onzas'")
        elif self.UNIDAD_MEDIDA_COMPRA == "Libras" and self.UNIDAD_MEDIDA_USO != "Libras" and self.UNIDAD_MEDIDA_USO != "Onzas":
            raise ValidationError("Si selecciona 'Libras' en el campo Unidad de compra, solo puede seleccionar 'Libras' u 'Onzas'")
    
        super().clean()

    def save(self, *args, **kwargs):
        if self.PRECIO_COMPRA > 0:
            if str(self.UNIDAD_MEDIDA_COMPRA) == str(self.UNIDAD_MEDIDA_USO):
                self.COSTO_UNITARIO = self.PRECIO_COMPRA / self.CANTIDAD
            elif str(self.UNIDAD_MEDIDA_COMPRA) == "Kilogramos" or str(self.UNIDAD_MEDIDA_COMPRA) == "Litros":
                self.COSTO_UNITARIO = self.PRECIO_COMPRA / self.CANTIDAD / 1000
            elif str(self.UNIDAD_MEDIDA_COMPRA) == "Libras":
                self.COSTO_UNITARIO = self.PRECIO_COMPRA / self.CANTIDAD / 16

        super(Insumo, self).save(*args, **kwargs)

class Receta(models.Model):
    CODIGO=models.AutoField(primary_key=True)
    NOMBRE=models.CharField(max_length=120,null=False,blank=False) 
    DETALLE=models.CharField(max_length=120,null=True,blank=True) 
    CANTIDAD_PORCIONES = models.DecimalField(max_digits=12,decimal_places=3,default=1,blank=False,null=False)
    COSTO_RECETA = models.DecimalField(max_digits=22,decimal_places=3,default=0,blank=True,null=True)
    COSTO_PORCION = models.DecimalField(max_digits=22,decimal_places=3,default=0,blank=True,null=True)
    GASTOS_ADICIONALES = models.DecimalField(max_digits=22,decimal_places=2,default=0,blank=False,null=False)
    RENTABILIDAD = models.DecimalField(max_digits=20,decimal_places=2,default=0,blank=True,null=True)
    PRECIO_VENTA = models.DecimalField(max_digits=22,decimal_places=2,default=1,blank=False,null=False)
    INGREDIENTES = models.ManyToManyField(Insumo)
    COSTO_FINAL = models.DecimalField(max_digits=22,decimal_places=2,default=0,blank=True,null=True)
    ULTIMA_ACTUALIZACION = models.DateTimeField(blank=True,null=True,auto_now=True)

    def __str__(self):
        return self.NOMBRE

    class Meta:
        verbose_name = 'Nuevo Producto'
        verbose_name_plural ='Lista de Precios' 

    def calcular_costo(self):
            costo = 0
            for ingrediente in self.INGREDIENTES.all():
                costo += ingrediente.COSTO_UNITARIO * ingrediente.CANTIDAD
            return costo
    
    def save(self, *args, **kwargs):
        
        if not self.pk:
             super(Receta, self).save(*args, **kwargs)

        costo_receta = 0
        self.COSTO_RECETA = 0
        self.COSTO_FINAL = 0

        for ingrediente in self.ingredientereceta_set.all():
            costo_receta += ingrediente.cantidad * ingrediente.pruducto.COSTO_UNITARIO
        
        gastos_adicionales = self.GASTOS_ADICIONALES
        costo_final = costo_receta + gastos_adicionales
        self.COSTO_RECETA = costo_receta
        self.COSTO_FINAL = costo_final

        self.COSTO_PORCION = self.COSTO_FINAL / self.CANTIDAD_PORCIONES

        rentabilidad = float(((self.PRECIO_VENTA - costo_final) / self.PRECIO_VENTA) * 100)
        self.RENTABILIDAD = rentabilidad

        super(Receta, self).save(*args, **kwargs)

        

class ingredientereceta(models.Model):

    pruducto  = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=20, decimal_places=2, default=1, blank=False, null=False)
    costo_unitario = models.DecimalField(max_digits=20, decimal_places=2,blank=True,null=True)
    medida_uso = models.CharField(max_length=255,blank=True,null=True)
    subtotal = models.DecimalField(max_digits=20,decimal_places=2,default=0,blank=False,null=False)

    class Meta:
        verbose_name = 'Insumos'
        verbose_name_plural ='Listado de Insumos' 

    def __str__(self):
        return self.receta.NOMBRE
    
    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("Por favor ingrese una cantidad superior a 0.")
        super().clean()

    def save(self, *args, **kwargs):
        self.costo_unitario = self.pruducto.COSTO_UNITARIO
        self.medida_uso = self.pruducto.UNIDAD_MEDIDA_USO
        self.subtotal = self.costo_unitario * self.cantidad
        
        super().save(*args, **kwargs)


