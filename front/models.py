from django.db import models

class Menu(models.Model):
    title = models.CharField("Название пункта меню", max_length=150)
    parent = models.ForeignKey("Menu", related_name="pid", on_delete=models.CASCADE, blank=True, null=True)
    href = models.CharField("Посилання", max_length=512)
    priority = models.IntegerField("Приоритет отображения", default=0)

class Page(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    text = models.TextField()
