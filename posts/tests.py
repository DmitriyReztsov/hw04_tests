from django.test import TestCase
from django.test import Client
from django.urls import reverse


from .models import User, Post


class Profile(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", 
                    email="test_user@krymskiy.com", 
                    password="1234!Q")
            
    def test_profile(self):
        response = self.client.get("/test_user/") # запрос к странице автора
        self.assertEqual(response.status_code, 200) # проверяем, что страница существует
        
    def new_post_auth(self):
        self.client.login(username='test_user', password='1234!Q')
        response = self.client.get("/new/")
        # проверяем, что там есть пост
        self.assertEqual(response.status_code, 200)

    def new_post_anonimus(self):
        response = self.client.get("/new/")
        self.assertNotEqual(response.status_code, 200)

    def after_pub(self):
        # создание поста зарегистрированным пользователем
        self.post = Post.objects.create(text="You're talking about things"
                    " I haven't done yet in the past tense. It's driving "
                    "me crazy!", author=self.user)
        # После публикации поста новая запись появляется на главной странице сайта (index)
        response = self.client.get(reverse('index'))
        paginator = response.context.get('paginator')
        post = response.context['page'][0]
        self.assertEqual(paginator.count, 1)
        self.assertEqual(post.text, self.post.text)

        # на персональной странице пользователя (profile),
        response = self.client.get(reverse('profile', args=(self.user.username,)))
        paginator = response.context.get('paginator')
        post = response.context['page'][0]
        self.assertEqual(paginator.count, 1)
        self.assertEqual(post.text, self.post.text)

        # и на отдельной странице поста (post)
        response = self.client.get(reverse('post', args=(self.user.username, self.post.id,)))
        #paginator = response.context.get('paginator')
        post = response.context['post']
        #self.assertEqual(paginator.count, 1)
        self.assertEqual(post.text, self.post.text)

    def edit_auth(self):
        self.client.login(username='test_user', password='1234!Q')
        self.post = Post.objects.create(text="Test text 1", author=self.user)
        
        # Авторизованный пользователь может отредактировать свой пост 
        response = self.client.get('/test_user/1/edit/')
        self.assertEqual(response.status_code, 200)
        self.post.text = "Test text 2"
        self.post.save()
        
        # и его содержимое изменится на всех связанных страницах: странице поста
        response = self.client.get('/test_user/1/')
        post = response.context['post']
        self.assertEqual(post.text, self.post.text)

        # на начальной странице (index)
        response = self.client.get(reverse('index'))
        post = response.context['page'][0]
        self.assertEqual(post.text, self.post.text)

        # на персональной странице пользователя (profile),
        response = self.client.get(reverse('profile', args=(self.user.username,)))
        post = response.context['page'][0]
        self.assertEqual(post.text, self.post.text)        
