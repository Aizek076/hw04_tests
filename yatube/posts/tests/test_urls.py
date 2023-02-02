from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.user_no_author = User.objects.create_user(username='no_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized = Client()
        self.authorized.force_login(PostURLTest.user)
        self.authorized_no_author = Client()
        self.authorized_no_author.force_login(PostURLTest.user_no_author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_accessibility_pages(self):
        """Проверка доступности главной, групп, профиля и поста"""
        url_names = [
            '/',
            f'/group/{PostURLTest.group.slug}/',
            f'/profile/{PostURLTest.user.username}/',
            f'/posts/{PostURLTest.post.pk}/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response_authorized = self.authorized.get(address)
                response_guest = self.client.get(address)
                self.assertEqual(
                    response_authorized.status_code, HTTPStatus.OK)
                self.assertEqual(
                    response_guest.status_code, HTTPStatus.OK)

    def test_urls_accessibility_edit_page(self):
        """Проверка доступности редактирования поста"""
        address = f'/posts/{PostURLTest.post.pk}/edit/'
        response_authorized = self.authorized.get(address)
        response_guest = self.client.get(address)
        response_authorized_no_author = (
            self.authorized_no_author.get(address))
        self.assertEqual(response_authorized.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response_guest,
            f'/auth/login/?next=/posts/{PostURLTest.post.pk}/edit/')
        self.assertEqual(
            response_authorized_no_author.url,
            f'/posts/{PostURLTest.post.pk}/')

    def test_urls_accessibility_create_page(self):
        """Проверка доступности создания поста"""
        address = '/create/'
        response_authorized = self.authorized.get(address)
        response_guest = self.client.get(address)
        self.assertEqual(response_authorized.status_code, HTTPStatus.OK)
        self.assertRedirects(response_guest, '/auth/login/?next=/create/')

    def test_urls_accessibility_unexisting_page(self):
        """Проверка доступности несуществующей страницы"""
        address = '/unexisting_page/'
        response_authorized = self.authorized.get(address)
        response_guest = self.client.get(address)
        self.assertEqual(response_authorized.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response_guest.status_code, HTTPStatus.NOT_FOUND)
