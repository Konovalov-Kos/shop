from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField("Название категории", max_length=200)
    parent = models.ForeignKey("Category", related_name="pid", on_delete=models.CASCADE, blank=True, null=True)

    @property
    def has_childs(self):
        return Category.objects.filter(parent=self).exists()

    @property
    def childs(self):
        return Category.objects.filter(parent=self)

    @property
    def products(self):
        return Product.objects.filter(category=self).order_by('-id')

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField("Имя бренда", max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "brand"

class Product(models.Model):
    name = models.CharField("Название", max_length=200)
    description = models.TextField()
    specification = models.TextField(default='')
    price = models.DecimalField("Цена", max_digits=11, decimal_places=2)
    prev_price = models.DecimalField("Пред. цена", max_digits=11, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    brand = models.ForeignKey("Brand", on_delete=models.CASCADE)
    image = models.CharField("Картинки", max_length=200, default='', null=True, blank=True)

    @property
    def image_url(self):
        if self.image:
            return "img/product/" + self.image
        else:
            return "img/product/nopicture.png"

    @property
    def prods_category_list(self):
        category = self.category
        mass = []
        while category.parent != None:
            mass.append(category)
            category = category.parent
        mass.append(category)
        mass.reverse()
        return mass

    def __str__(self):
        return self.name