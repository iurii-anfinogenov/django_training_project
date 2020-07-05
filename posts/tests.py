from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Post, User


class TestStringMethods(TestCase):
    def test_length(self):
        self.assertEqual(len('yatube'), 6)


class TestYatubeGeneral(TestCase):
    def setUp(self):
        self.client_not_auth = Client()
        self.client = Client()
        self.user = User.objects.create(username='user', password='12345')
        self.client.force_login(self.user)
        self.text = 'new post auth user'
        self.newtext = 'changed text'

    def check_post(self, url, text):
        self.response = self.client.get(reverse(url), follow=True)
        return self.assertContains(self.response, text)

    def test_check_redirect_not_auth_user(self):
        response = self.client_not_auth.get(reverse('new_post'), follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')
        self.post = self.client_not_auth.post(
            reverse('new_post'), {'text': self.text})
        post_count = Post.objects.filter(text=self.text).count()
        self.assertNotEqual(post_count, 1)

    def test_create_profile_new_user(self):
        response = self.client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_auth_user_create_post(self):
        self.client.post(reverse('new_post'), {'text': self.text})
        self.check_post('index', self.text)

        post_count = Post.objects.filter(text=self.text).count()
        self.assertEqual(post_count, 1)

    def test_post_create_allowed_pages(self):
        self.post = Post.objects.create(text=self.text, author=self.user)
        self.check_post('index', self.text)

        response = self.client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        self.assertContains(response, self.text)

        response = self.client.get(reverse(
            'post', kwargs={'username': self.user.username,
                            'post_id': self.post.id}))
        self.assertContains(response, self.text)

    def test_user_change_post(self):
        self.post = Post.objects.create(text=self.text, author=self.user)
        self.client.post(reverse('post_edit',  kwargs={
                         'username': self.user.username,
                         'post_id': self.post.id}), {'text': self.newtext})
        self.check_post('index', self.newtext)

        response = self.client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        self.assertContains(response, self.newtext)

        response = self.client.get(reverse(
            'post',
            kwargs={'username': self.user.username, 'post_id': self.post.id}))
        self.assertContains(response, self.newtext)

    def test_404(self):
        response = self.client.get(
            reverse('profile', kwargs={'username': 'test'}))
        self.assertEqual(response.status_code, 404)

    def test_505(self):
        response = self.client.get(reverse('server_error'))
        self.assertEqual(response.status_code, 500)

    def test_img_check_load(self):
        with open('posts/file.jpg','rb') as img:
...         post = self.client.post(
                "<username>/<int:post_id>/edit/",
                 {'author': self.user, 'text': 'post with image', 'image': img})
