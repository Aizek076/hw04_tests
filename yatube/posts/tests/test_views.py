from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test_slug_2',
            description='Тестовое описание',
        )
        cls.group_3 = Group.objects.create(
            title='Тестовая группа_3',
            slug='test_slug_3',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group_2,
        )

    def setUp(self):
        self.guest = Client()
        self.authorized = Client()
        self.authorized.force_login(PostViewsTest.user)

    def test_index_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.author.username, 'author')
        self.assertEqual(first_object.group.title, 'Тестовая группа')

    def test_index_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized.get(reverse(
            'posts:group_list', kwargs={'slug': PostViewsTest.group.slug}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.author.username, 'author')
        self.assertEqual(first_object.group.title, 'Тестовая группа')
        self.assertEqual(response.context['group'].title, 'Тестовая группа')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized.get(reverse(
            'posts:profile', kwargs={'username': PostViewsTest.user.username}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.author.username, 'author')
        self.assertEqual(first_object.group.title, 'Тестовая группа')
        self.assertEqual(response.context['author'].username, 'author')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized.get(reverse(
            'posts:post_detail', kwargs={'post_id': PostViewsTest.post.pk}))
        first_object = response.context['posts']
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.author.username, 'author')
        self.assertEqual(first_object.group.title, 'Тестовая группа')

    def test_post_edit_detail_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized.get(reverse(
            'posts:post_edit', kwargs={'post_id': PostViewsTest.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_detail_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_in_pages(self):
        """Проверка создания поста на главной, группе, в профайле"""
        templates_page_names = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTest.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': PostViewsTest.user.username})
        ]
        for page in templates_page_names:
            with self.subTest(page=page):
                response = self.authorized.get(page)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object, PostViewsTest.post)

    def test_post_create_in_his_group(self):
        """Проверка созданного поста на принадлежащую группу"""
        response = self.authorized.get(reverse(
            'posts:group_list',
            kwargs={'slug': PostViewsTest.group_2.slug}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, PostViewsTest.post_2)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            [Post(
                text=f"Пост {i}",
                author=cls.user,
                group=cls.group)
                for i in range(13)])

    def setUp(self):
        self.authorized = Client()
        self.authorized.force_login(self.user)

    def test_post_paginator(self):
        """Проверка paginator"""
        posts_on_first_page = 10
        posts_on_second_page = 3
        templates_page_names = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        ]
        for page in templates_page_names:
            with self.subTest(page=page):
                # response_1 = self.authorized.get(page)
                # response_2 = self.authorized.get(page + '?page=2')
                self.assertEqual(len(self.authorized.get(
                    page).context.get('page_obj')),
                    posts_on_first_page)
                self.assertEqual(len(self.authorized.get(
                    page + '?page=2').context.get('page_obj')),
                    posts_on_second_page)
