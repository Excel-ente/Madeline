from .models import Receta
from django.contrib import admin


@admin.action(description="Actualizar")
def Actualizar(modeladmin, request, queryset):

    for receta in Receta.objects.all():

        costo_receta = 0
        gastos_adicionales = receta.GASTOS_ADICIONALES

        for ingrediente in receta.ingredientereceta_set.all():
            costo_receta += ingrediente.cantidad * ingrediente.costo_unitario

        receta.COSTO_RECETA = costo_receta 
        receta.COSTO_FINAL = costo_receta + gastos_adicionales
        receta.save()
