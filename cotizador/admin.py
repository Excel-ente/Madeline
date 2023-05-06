from django.contrib import admin
from .models import Insumo,Receta,ingredientereceta
from .Funciones import Actualizar
from import_export.admin import ImportExportModelAdmin
import pytz


# Register your models here.

admin.site.site_header = "Cotizador de Recetas"
admin.site.site_title = "Cotizador de Recetas"


@admin.register(Insumo)
class InventarioAdmin(ImportExportModelAdmin):
    list_display = ('PRODUCTO', 'UNIDAD_MEDIDA_COMPRA', 'CANTIDAD', 'PRECIO__COMPRA', 'UNIDAD_MEDIDA_USO', 'COSTO__UNITARIO',)
    ordering = ('PRODUCTO',)
    list_filter=()
    exclude=('COSTO_UNITARIO','STOCK',)
    search_fields = ('PRODUCTO',)
    list_per_page = 25
    list_display_links = ('PRODUCTO',)
    
    def PRECIO__COMPRA(self, obj):
        return "💲{:,.2f}".format(obj.PRECIO_COMPRA)
    
    def COSTO__UNITARIO(self, obj):
        return "💲{:,.2f}".format(obj.COSTO_UNITARIO)


class IngredienteRecetaInline(admin.TabularInline):
    model = ingredientereceta
    extra = 1
    fields = ('pruducto', 'cantidad','medida_uso','subtotal',)
    readonly_fields =('medida_uso','subtotal',)


@admin.register(Receta)
class RecetaAdmin(ImportExportModelAdmin):
    inlines = [
        IngredienteRecetaInline,
    ]
    list_display = ('NOMBRE','Costo_Final','Costo_Porcion','Precio_Venta','Rentabilidad','Ultima_Actualizacion',)
    ordering = ('RENTABILIDAD',)
    exclude=('STOCK','COSTO_RECETA','INGREDIENTES','ULTIMA_ACTUALIZACION',)
    search_fields = ('NOMBRE',)
    list_per_page = 25
    list_display_links = ('NOMBRE',)
    readonly_fields=('RENTABILIDAD','COSTO_FINAL','COSTO_PORCION',)
    actions=[Actualizar,]
    

    def Costo_Porcion(self, obj): 
        formateo = "💲{:,.2f}".format(obj.COSTO_PORCION)
        return formateo
    
    def Costo_Final(self, obj): 
        formateo = "💲{:,.2f}".format(obj.COSTO_FINAL)
        return formateo
    
    def Precio_Venta(self, obj):
        formateo = "💲{:,.2f}".format(obj.PRECIO_VENTA)
        return formateo
    
    def Rentabilidad(self, obj):
        if obj.RENTABILIDAD > 0:
            formateo = "📊 " + str(obj.RENTABILIDAD)
        else:
            formateo = "🔻 " + str(obj.RENTABILIDAD)
        return formateo

    def Ultima_Actualizacion(self, obj): 
        hora_buenos_aires = pytz.timezone('America/Argentina/Buenos_aires')
        fecha_hora = obj.ULTIMA_ACTUALIZACION.astimezone(hora_buenos_aires)
        formateo = fecha_hora.strftime("%H:%M %d/%m/%Y")

        formateo = "📆 " +formateo
        return formateo

