from django.contrib import admin
from .models import Category, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    class Meta:
        managed = True
        verbose_name = "категория"
        verbose_name_plural = "Категории"


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    class Meta:
        managed = True
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    class Meta:
        managed = True
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
