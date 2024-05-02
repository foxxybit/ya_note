from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note

User = get_user_model()


class ReaderMixin(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Винсент Лоу')


class AuthorLoginMixin(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Риэл Мэйер')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)


class ReaderLoginMixin(ReaderMixin):

    @classmethod
    def setUpTestData(cls):
        ReaderMixin.setUpTestData()
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)


class NoteMixin(AuthorLoginMixin):

    @classmethod
    def setUpTestData(cls):
        AuthorLoginMixin.setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test',
            author=cls.author
        )
