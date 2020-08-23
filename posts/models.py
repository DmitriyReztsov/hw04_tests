from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


"""Создание модели сообществ.

Заложена возможность публиковать посты без привязки к сообществам
(blank=True, null=True).

"""
class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=40, unique=True, blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        """Вывод на экран названия сообщества"""
        return self.title


"""Создание модели постов блога""" 
class Post(models.Model):
    text = models.TextField(verbose_name="Текст", help_text="Напечатайте "
                            "свое произведение здесь.")
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, 
                              null=True, related_name="post", 
                              verbose_name="Тема", help_text="Выберите тему.")
    
    class Meta:
        ordering = ['-pub_date']  # упорядочивание записей в модели
 