from django.test import TestCase
from django.test import Client
from django.urls import reverse


from .models import User, Post, Group


class Profile(TestCase):
    def setUp(self):
        self.client_auth = Client()
        self.user = User.objects.create_user(username="test_user", 
                    email="test_user@krymskiy.com", 
                    password="1234!Q")
        self.group = Group.objects.create(
                    title="test_group", 
                    slug="testgroup", 
                    description="test description"
                    )
        self.client_auth.force_login(self.user)
        self.client_non = Client()

    # метод для проверки постов
    def check_text(self, post1, post2):
        # check text
        self.assertEqual(post1.text, post2.text)
        # chek author
        self.assertEqual(post1.author, post2.author)
        # check group
        self.assertEqual(post1.group, post2.group)

    def check_urls(self, post1):
        urls = (
		    reverse("index"),
		    reverse("profile", kwargs={"username": self.user.username}),
		    reverse("post", kwargs={"username": self.user.username, "post_id": self.post.id,})
	    )
        for url in urls:
            response = self.client_non.get(url)
            if url == reverse("post", kwargs={"username": self.user.username, "post_id": self.post.id,}):
                post_new = response.context['post']
            else:
                paginator = response.context.get('paginator')
                post_new = response.context['page'][0]
                self.assertEqual(paginator.count, 1)
            self.check_text(self.post, post_new)

    def test_profile(self):
        # запрос к странице автора
        response = self.client_non.get(reverse('profile', 
                    kwargs={"username": self.user.username,})) 
        # проверяем, что страница существует
        self.assertEqual(response.status_code, 200) 
        
    def test_new_post_auth(self):
        # снимаем количество постов до создания нового поста
        posts_before = Post.objects.count()
        # create new post
        self.post = Post.objects.create(
                    text="Test text", 
                    author=self.user, 
                    group=self.group
                    )
        # get quantity of posts after post creation
        posts_after = Post.objects.count()
        post_new = Post.objects.get(id=1)
        response = self.client_auth.get(reverse('new_post'))
        # проверяем, что есть доступ к странице создания поста
        self.assertEqual(response.status_code, 200)
        # check new post added to DB
        self.assertNotEqual(posts_before, posts_after)
        self.check_text(self.post, post_new)

    def test_new_post_anonimus(self):
        # снимаем количество постов до попытки создания нового поста
        posts_before = Post.objects.count()
        response = self.client_non.get(reverse('new_post'))
        # get quantity of posts after post creation attemp
        posts_after = Post.objects.count()
        self.assertRedirects(response, '/auth/login/?next=/new/')
        self.assertEqual(posts_before, posts_after)

    def test_after_pub(self):
        # создание поста зарегистрированным пользователем
        self.post = Post.objects.create(text="You're talking about things"
                    " I haven't done yet in the past tense. It's driving "
                    "me crazy!", author=self.user)
        # Проверка после публикации на связанных страницах
        self.check_urls(self.post)

    def test_edit_auth(self):
        self.post = Post.objects.create(text="Test text 1", author=self.user)
        
        # Авторизованный пользователь может отредактировать свой пост 
        response = self.client_auth.get(reverse('post_edit', 
                    kwargs={"username": self.user.username, "post_id": self.post.id,}))
        self.assertEqual(response.status_code, 200)
        self.post.text = "Test text 2"
        self.post.save()
        
        # Проверка после публикации на связанных страницах
        self.check_urls(self.post)
