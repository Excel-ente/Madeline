from django.contrib import admin
from .models import *
from datetime import timedelta
from django.utils import timezone   
from import_export.admin import ImportExportModelAdmin
from .AccionesOrden import *

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('NOMBRE_Y_APELLIDO','EMAIL','TELEFONO','PEDIDOS_TOTALES','FECHA_PROXIMA_ENTREGA',)
    exclude = ('PEDIDOS_TOTALES','PEDIDOS_ENTREGADOS','PEDIDOS_PENDIENTES',)
    readonly_fields = ('FECHA_PROXIMA_ENTREGA',)


@admin.register(Estado)          
class EstadoAdmin(ImportExportModelAdmin):
    list_display = ('ESTADO',)

class RecetaOrdenInline(admin.TabularInline):
    model = ArticuloOrden
    extra = 1
    fields = ('receta','cantidad','Precio_','Subtotal_','fecha_ultimo_costo','Ganancias_',)
    readonly_fields=('costo_receta','fecha_ultimo_costo','Precio_','Ganancias_','Subtotal_',)
    can_delete=True

    def Precio_(self, obj): 
        formateo = "💲{:,.2f}".format(obj.precio)
        return formateo

    def Subtotal_(self, obj): 
        formateo = "💲{:,.2f}".format(obj.subtotal)
        return formateo
    
    def Ganancias_(self, obj): 
        formateo = "💲{:,.2f}".format(obj.ganancia)
        return formateo


class FechaEntregaFilter(admin.SimpleListFilter):
    title = 'Fecha de entrega'
    parameter_name = 'fecha_entrega'

    def lookups(self, request, model_admin):
        return (
            ('Hoy', 'Hoy'),
            ('3dias', 'Próximos 3 días'),
            ('7dias', 'Próximos 7 días'),
            ('30dias', 'Próximos 30 días'),
        )

    def queryset(self, request, queryset):
        now = timezone.now().date()
        
        if self.value() == '3dias':
            fecha_limite = now + timedelta(days=3)
            return queryset.filter(fecha_entrega__range=[now, fecha_limite])
        elif self.value() == '7dias':
            fecha_limite = now + timedelta(days=7)
            return queryset.filter(fecha_entrega__range=[now, fecha_limite])
        elif self.value() == '30dias':
            fecha_limite = now + timedelta(days=30)
            return queryset.filter(fecha_entrega__range=[now, fecha_limite])
        elif self.value() == 'Hoy':
            fecha_limite = now
            return queryset.filter(fecha_entrega__range=[now, fecha_limite])
        else:
            return queryset


@admin.register(Orden)
class OrdenAdminAdmin(admin.ModelAdmin):
    
    inlines = [
    RecetaOrdenInline,
    ]

    list_display = ('estado','cliente','Total_Pedido','Pendiente_de_pago','fecha_entrega','aclaraciones',)
    readonly_fields=('Total_Pedido','Pendiente_de_pago','Anticipo','estado',)
    ordering=('fecha_entrega',)
    exclude=('adelanto','fecha_creacion','estado','debe',)
    list_filter = (FechaEntregaFilter, 'estado', )
    actions=[actualizar_costos_articulos_orden,Iniciar_Pedido,Terminar_Pedido,Cancelar_Pedido,Entregar_Pedido,]

    def Pendiente_de_pago(self, obj): 
        formateo = "💲{:,.2f}".format(obj.debe)
        return formateo

    def Total_Pedido(self, obj): 
        formateo = "💲{:,.2f}".format(obj.total)
        return formateo

    def Anticipo(self, obj): 
        formateo = "💲{:,.2f}".format(obj.adelanto)
        return formateo

    def Telefono_(self, obj):
        formateo = "📲 " + str(obj.TELEFONO)
        return formateo
    def Ordenes_Entregadas(self, obj):
        formateo = "📦 " + str(obj.PEDIDOS_ENTREGADOS)
        return formateo
    def Ordenes_Por_Entregar(self, obj):
        formateo = "⌛ " + str(obj.PEDIDOS_PENDIENTES)
        return formateo
    def Proxima_entrega(self, obj):
        formateo = "📆 " + str(obj.FECHA_PROXIMA_ENTREGA)
        return formateo
    

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('fecha','cliente','orden_asociada','Pago','Total_Orden','Restante',)
    ordering = ('fecha',)
    exclude=('total_orden','deuda_pendiente','fecha_vencimiento',)
    search_fields = ('cliente',)
    list_per_page = 50
    list_display_links = ('cliente',)

    def Pago(self, obj):    
        formateo = "💲{:,.2f}".format(obj.pago)
        return formateo
    
    def Total_Orden(self, obj):    
        formateo = "💲{:,.2f}".format(obj.total_orden)
        return formateo
    
    def Restante(self, obj):    
        formateo = "💲{:,.2f}".format(obj.deuda_pendiente)
        return formateo
    

@admin.register(Retiro)
class RetiroAdmin(ImportExportModelAdmin):
    list_display = ('fecha','detalle','Total_Retirado',)
    list_display_links=('fecha',)
    exclude=('codigo_retiro','fecha',)
    list_filter=('fecha',)
    ordering=('fecha',)

    def Total_Retirado(self, obj):
        return "💵 ${:,.2f}".format(obj.total)
    

@admin.register(Gasto)
class RetiroAdmin(ImportExportModelAdmin):
    list_display = ('fecha','detalle','Total_Gasto',)
    list_display_links=('fecha',)
    exclude=('codigo_gasto','fecha',)
    list_filter=('fecha',)
    ordering=('fecha',)

    def Total_Gasto(self, obj):
        return "💵 ${:,.2f}".format(obj.pago)
    
@admin.register(CierreCaja)
class CierreCajaAdmin(ImportExportModelAdmin):
    list_display = ('fecha','Dinero_inicial','Ingresos','Salidas','Dinero_al_Cierre','Diferencias_',)
    list_display_links=('fecha',)
    list_filter=('fecha',)
    ordering=('fecha',)
    exclude = ('numero_reporte','total_ventas','pagos_clientes','gastos','retiros_efectivo','final','diferencias','efectivo_inicial',)

    def Dinero_inicial(self,obj):
        return "${:,.2f}".format(obj.efectivo_inicial)

    def Ingresos(self, obj):
        return "${:,.2f}".format(obj.pagos_clientes)

    def Salidas(self, obj):
        salida = obj.gastos + obj.retiros_efectivo
        return "${:,.2f}".format(salida)

    def pagos_de_clientes(self, obj):
        return "${:,.2f}".format(obj.pagos_clientes)
    
    def Dinero_al_Cierre(self, obj):
        return "${:,.2f}".format(obj.final)
    
    def Diferencias_(self, obj):
        return "${:,.2f}".format(obj.diferencias)
    
