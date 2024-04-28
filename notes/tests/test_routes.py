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

    def test_pages_aviability(self):
        """Проверяет доступность страниц для анонимного пользователя."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note(self):
        """Проверяет доступность страниц для залогиненных пользователей."""
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

            url = reverse('notes:list')
            self.client.force_login(self.author)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяет перенаправление анонимного пользователя с недоступных
        для него страниц.
        """
        login_url = reverse('users:login')
        for name in (
            'notes:list',
            'notes:edit',
            'notes:delete',
            'notes:detail'
        ):
            with self.subTest(name=name):
                if name == 'notes:list':
                    url = reverse(name)
                else:
                    url = reverse(name, args=[self.note.slug])
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
