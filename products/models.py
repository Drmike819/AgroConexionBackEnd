from django.db import models

# Create your models here.

# creacion del modelo para las categorias
class Category(models.Model):
    # nombre de la categoria debe ser unico y es requerido
    name = models.CharField(max_length=50, blank=False, null=False, unique=True)
    # descripcion de la categoria debe ser requerido
    description = models.TextField(blank=False, null=False)
    
    # retornamos en nombre de la categoria
    def __str__(self):
        return self.name
    

# creaciond del modelo producto
class Products(models.Model):
    # nombre del producto es obligatorio
    name = models.CharField(max_length=100, null=False, blank=False)
    # descripcion del producto debe ser obligatorio
    description = models.TextField(null=False, blank=False)
    # precio del productp debe ser obligatorio
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    # cantidad de producto disponible, debe ser obligatorio
    stock = models.IntegerField(null=False, blank=False)
    
    # lista de tupla que se utiliza para restrinigr las opciones de  la unidad de medida
    UNIT_CHOICES = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('unidad', 'Unidad'),
        ('li', 'libra'),
    ]
    # los unicos valores permintido seran los mostrados en la lista de tuplas
    unit_of_measure = models.CharField(max_length=10, choices=UNIT_CHOICES, default='unidad')
    # categorias del producto, esta tiene una relacion muchos a muchos
    category = models.ManyToManyField(Category, related_name="category_products")
    # este sera el "autor" del producto
    producer = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name="producer_products")
    # fecha del dia y la hora de la creacion del producto
    date_of_registration = models.DateTimeField(auto_now=True)
    # lista de tupla que se utiliza para restrinigr las opciones del estado del producto
    STATUS_CHOICES = [
        ('disponible', 'Disponible'),
        ('agotado', 'Agotado'),
        ('inactivo', 'Inactivo'),
    ]
     # los unicos valores permintido seran los mostrados en la lista de tupla
    state = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponible')
    
    def save(self, *args, **kwargs):
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")
        super().save(*args, **kwargs)
        
    # retorna el nombre del producto
    def __str__(self):
        return self.name

# modelo que almacenara multiples imagenes para un producto
class ProductImage(models.Model):
    # identidicador del producto
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="images")
    # imagen del producto
    image = models.ImageField(upload_to="products_pictures/")

    # retornamos el nombre del producto a la cuial pertenece la imagen
    def __str__(self):
        return f"Imagen de {self.product.name}"