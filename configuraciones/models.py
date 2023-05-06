from django.db import models

# Create your models here.

class Rutas_Descarga(models.Model):
    NOMBRE=models.CharField(max_length=50,null=False,blank=False)
    RUTA_DESCARGA=models.CharField(max_length=120,null=False,blank=False)

    def __str__(self):
        return self.NOMBRE
    
    class Meta:
        verbose_name = 'Variable'
        verbose_name_plural ='Variables' 

class DineroInicial(models.Model):
    importe=models.DecimalField(max_digits=20,decimal_places=2,blank=False,null=False)

    def __str__(self):
        return self.importe