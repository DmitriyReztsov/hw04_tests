from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """Создаем класс формы на базе модели Post
       для добавления в Post новых записей"""
    class Meta:
        model = Post
        fields = ['group', 'text']
