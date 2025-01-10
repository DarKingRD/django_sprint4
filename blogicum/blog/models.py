from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Information(models.Model):
    id = models.AutoField(primary_key=True)
    is_published = models.BooleanField(
        default=True,
        blank=False,
        null=False,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Добавлено",
    )

    class Meta:
        abstract = True


class Category(Information):
    title = models.CharField(
        max_length=256, blank=False, verbose_name="Заголовок")
    description = models.TextField(blank=False, verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        blank=False,
        verbose_name="Идентификатор",
        help_text="Идентификатор страницы для URL;\
 разрешены символы латиницы, цифры, дефис и подчёркивание.",
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = ""
        managed = True
        verbose_name = "категория"
        verbose_name_plural = "Категории"


class Location(Information):
    name = models.CharField(max_length=256, blank=False,
                            verbose_name="Название места")

    def __str__(self):
        return self.name

    class Meta:
        db_table = ""
        managed = True
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"


class Post(Information):
    title = models.CharField(
        max_length=256, blank=False, verbose_name="Заголовок")
    text = models.TextField(blank=False, verbose_name="Текст")
    pub_date = models.DateTimeField(
        blank=False,
        verbose_name="Дата и время публикации",
        help_text="Если установить дату и время в будущем —\
 можно делать отложенные публикации.",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=False,
        verbose_name="Автор публикации"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name="Местоположение",
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=False,
        verbose_name="Категория",
        null=True,
    )
    image = models.ImageField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = ""
        ordering = ("-pub_date",)
        managed = True
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"


class Comment(Information):
    text = models.TextField(
        verbose_name="Текст комментария", help_text="Введите текст комментария"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Публикация",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор")

    class Meta:
        ordering = ("created_at",)
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text[:50]
