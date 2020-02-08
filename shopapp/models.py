from django.contrib.auth.models import User
from django.db import models
import datetime
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
    description = models.TextField(blank=True, null=True)
    specification = models.TextField(default='', blank=True, null=True)
    price = models.DecimalField("Цена", max_digits=11, decimal_places=2)
    prev_price = models.DecimalField("Пред. цена", max_digits=11, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    brand = models.ForeignKey("Brand", on_delete=models.CASCADE)
    image = models.CharField("Картинки", max_length=200, default='', null=True, blank=True)
    add_date = models.DateTimeField(auto_now_add=False, default=datetime.datetime.now)

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

class Order(models.Model):
    NEW_ORDER = 0
    IN_PROGRES = 1
    DELIVERED = 2
    AVAIL_STATUSES = [
        (NEW_ORDER, 'Заказ готов к оплате'),
        (IN_PROGRES, 'Отправлен'),
        (DELIVERED, 'Доставлен'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=AVAIL_STATUSES,
        default=NEW_ORDER,
    )
    modify_date = models.DateTimeField(auto_now=True)
    price_to_pay = models.DecimalField("Цена заказа", max_digits=11, decimal_places=2)
    phone = models.CharField("Телефон", max_length=50)
    delivery_adress = models.TextField()
    comment = models.TextField(blank=True, null=True)

    @property
    def products(self):
        return ProductsInOrders.objects.filter(order=self)

class ProductsInOrders(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    price = models.DecimalField("Цена", max_digits=11, decimal_places=2)
    kvo = models.IntegerField("Количество")

class News(models.Model):
    name = models.CharField("Новость", max_length=100)
    shorttext = models.CharField('Текст новости', max_length=300)
    news_img = models.CharField("Картинка новости", max_length=200, default='', null=True, blank=True)
    news_date = models.DateTimeField(auto_now=True)