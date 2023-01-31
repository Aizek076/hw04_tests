from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

from time import sleep

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
        for i in range(12):
            Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Тестовый пост',
            )
            sleep(0.001)

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

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTest.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTest.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author.username
        task_group_0 = first_object.group.title
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_author_0, 'author')
        self.assertEqual(task_group_0, 'Тестовая группа')

    def test_index_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized.get(reverse(
            'posts:group_list', kwargs={'slug': PostViewsTest.group.slug}))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author.username
        task_group_0 = first_object.group.title
        task_group_title_0 = response.context['group'].title
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_author_0, 'author')
        self.assertEqual(task_group_0, 'Тестовая группа')
        self.assertEqual(task_group_title_0, 'Тестовая группа')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized.get(reverse(
            'posts:profile', kwargs={'username': PostViewsTest.user.username}))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author.username
        task_group_0 = first_object.group.title
        task_author_context_0 = response.context['author'].username
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_author_0, 'author')
        self.assertEqual(task_group_0, 'Тестовая группа')
        self.assertEqual(task_author_context_0, 'author')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized.get(reverse(
            'posts:post_detail', kwargs={'post_id': PostViewsTest.post.pk}))
        first_object = response.context['posts']
        task_text_0 = first_object.text
        task_author_0 = first_object.author.username
        task_group_0 = first_object.group.title
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_author_0, 'author')
        self.assertEqual(task_group_0, 'Тестовая группа')

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

    def test_post_paginator(self):
        """Проверка paginator"""
        templates_page_names = {
            reverse('posts:index'): 4,
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTest.group.slug}): 10,
            reverse('posts:profile',
                    kwargs={'username': PostViewsTest.user.username}): 4
        }
        for page, page_2 in templates_page_names.items():
            with self.subTest(page=page):
                response_1 = self.authorized.get(page)
                response_2 = self.authorized.get(page + '?page=2')
                self.assertEqual(len(response_1.context['page_obj']), 10)
                self.assertEqual(len(response_2.context['page_obj']), page_2)
