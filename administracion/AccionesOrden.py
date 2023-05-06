from .models import Orden
from django.contrib import admin
from django.contrib import messages

@admin.action(description="Actualizar Pedidos Sin Entregar")
def actualizar_costos_articulos_orden(modeladmin, request, queryset):
    
    pedidos = Orden.objects.all()   

    for pedido in pedidos:

        pedido.save()



@admin.action(description="Iniciar Pedido")
def Iniciar_Pedido(modeladmin, request, queryset):
    for orden in queryset:
        if orden.estado_id==6:
            messages.error(request, "No se puede modificar un pedido cancelado.") 
        else:
            if orden.estado.ESTADO=="Recibido" or orden.estado.ESTADO=="En Espera":
                orden.estado_id = 2
                orden.save()
            else:
                messages.error(request, "Para iniciar el pedido la orden debe estar en Recibido o En Espera.") 

       

@admin.action(description="Terminar Pedido")
def Terminar_Pedido(modeladmin, request, queryset):
    for orden in queryset:
        if orden.estado_id==6:
            messages.error(request, "No se puede modificar un pedido cancelado.") 
        else:
            if orden.estado.ESTADO=="En Proceso":
                orden.estado_id = 3
                orden.save()
            else:
                messages.error(request, "El pedido debe estar en proceso para ser finalizado.") 




@admin.action(description="Entregar Pedido")
def Entregar_Pedido(modeladmin, request, queryset):
    for orden in queryset:
        if orden.estado_id==6:
            messages.error(request, "No se puede modificar un pedido cancelado.") 
        else:
            if orden.estado.ESTADO=="Listo Para Entregar":
                orden.estado_id = 4
                orden.save()
            else:
                messages.error(request, "El pedido debe estar en Listo para Entregar para ser entregado.") 

@admin.action(description="Cancelar Pedido")
def Cancelar_Pedido(modeladmin, request, queryset):
    for orden in queryset:
        if orden.estado_id==6:
            messages.error(request, "No se puede modificar un pedido cancelado.") 
        else:
            orden.estado_id = 6 
            orden.save()
