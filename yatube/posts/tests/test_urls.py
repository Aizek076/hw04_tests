from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


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
        self.guest = Client()
        self.authorized = Client()
        self.authorized.force_login(PostURLTest.user)
        self.authorized_no_author = Client()
        self.authorized_no_author.force_login(PostURLTest.user_no_author)

    def test_urls_uses_correct_template(self):
        """Проверка вызываемых HTML-шаблонов"""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTest.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTest.user.username}/': 'posts/profile.html',
            f'/posts/{PostURLTest.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{PostURLTest.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized.get(address)
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
                response_guest = self.guest.get(address)
                self.assertEqual(response_authorized.status_code, 200)
                self.assertEqual(response_guest.status_code, 200)

    def test_urls_accessibility_edit_page(self):
        """Проверка доступности редактирования поста"""
        address = f'/posts/{PostURLTest.post.pk}/edit/'
        response_authorized = self.authorized.get(address)
        response_guest = self.guest.get(address)
        response_authorized_no_author = (
            self.authorized_no_author.get(address))
        self.assertEqual(response_authorized.status_code, 200)
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
        response_guest = self.guest.get(address)
        self.assertEqual(response_authorized.status_code, 200)
        self.assertRedirects(response_guest, '/auth/login/?next=/create/')

    def test_urls_accessibility_unexisting_page(self):
        """Проверка доступности несуществующей страницы"""
        address = '/unexisting_page/'
        response_authorized = self.authorized.get(address)
        response_guest = self.guest.get(address)
        self.assertEqual(response_authorized.status_code, 404)
        self.assertEqual(response_guest.status_code, 404)
