from http import HTTPStatus


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Наруто Удзумаки')
        cls.reader = User.objects.create(username='Саске Учиха')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_pages_aviability_for_anonymous_client(self):
        for name in (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        ):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=[self.note.slug])
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:edit', [self.note.slug]),
            ('notes:delete', [self.note.slug]),
            ('notes:detail', [self.note.slug]),
            ('notes:success', None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test__pages_aviability_for_autorized_client(self):
        self.client.force_login(self.author)
        for name in (
            'notes:home',
            'notes:add',
            'notes:success',
            'users:login',
            'users:logout',
            'users:signup',
        ):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
