from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
#  функция reverse_lazy позволяет получить URL по параметру "name" функции path()
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm


"""Функция вывода главной страницы"""
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "index.html", {'page': page, 'paginator': paginator})


"""view-функция для страницы сообщества"""
def group_posts(request, slug):
    """функция get_object_or_404 получает по заданным критериям объект из 
    базы данных или возвращает сообщение об ошибке, если объект не найден.
    Далее получаем посты с общим свойством group через related_name.

    """
    group = get_object_or_404(Group, slug=slug)
    post_list = group.post.all()  # упорядочено по дате в модели
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением    
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})

""" view-функция для обработки нового поста"""
def new_post(request):
    if request.user.is_authenticated == False:
        return redirect ('index')
    
    """ Проверка метода, валидация и сохранения формы.

    Если метод не POST (GET), если форма не прошла валидацию - 
    возвращается страница с формой и заполненными данными, прошедшими валидацию.

    """
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'new_post.html', {'form': form})
        
    form = PostForm(request.POST)
        
    if form.is_valid() == False:
        return render(request, 'new_post.html', {'form': form})

    # сохраняем форму, оставляя ее доступной для редактирования
    # определяем оставшееся обязательное поле author, сохраняем
    new_entry = form.save(commit=False)
    new_entry.author = request.user
    new_entry.save()
    return redirect('index')

def profile(request, username):
    profile_user = User.objects.get(username=username)
    profile_posts = Post.objects.filter(author=profile_user)
    paginator = Paginator(profile_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html',
                 {"profile_user": profile_user, 
                  'profile_posts': profile_posts, 'page': page,
                   'paginator': paginator}
                 )
 
 
def post_view(request, username, post_id):
    post = Post.objects.get(pk=post_id)
    author = User.objects.get(username=username)
    quantity_posts = Post.objects.filter(author=author).count
    return render(request, 'post.html', {'author': author, 'post': post, 'quantity_posts': quantity_posts})


def post_edit(request, username, post_id):
    author = User.objects.get(username=username)
    article = Post.objects.get(id=post_id) # запрашиваем объект

    # проверка что текущий пользователь — это автор записи
    if request.user != author:
        return post_view(request, author, article.id)

    if request.method != 'POST':
        form = PostForm(instance=article) # передаём запрошенный объект в форму
        # отрисовываем форму с заполненным постом
        if_edit = True
        return render(request, 'new_post.html', {'form': form, 'if_edit': if_edit, 
                        'article': article}) # article нужна для прохождения тестов
        
    form = PostForm(request.POST)
        
    if form.is_valid() == False:
        return render(request, 'new_post.html', {'form': form})

    # сохраняем форму, оставляя ее доступной для редактирования
    # определяем оставшиеся поля author, id, pub_date, сохраняем
    edited_entry = form.save(commit=False)
    edited_entry.author = author
    edited_entry.id = article.id
    edited_entry.pub_date = article.pub_date
    edited_entry.save()
    return redirect('post', username=author, post_id=article.id)