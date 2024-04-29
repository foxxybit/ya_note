from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestFormAndListPages(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Аска Лэнгли')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Рей Аянами')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        readers_notes = [
            Note(
                title='Заголовок',
                text='Текст',
                slug=f'slug_{index}',
                author=cls.reader
            )
            for index in range(5)
        ]
        cls.reader_list = Note.objects.bulk_create(readers_notes)
        cls.list_url = reverse('notes:list')

    def test_autorized_client_has_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', [self.note.slug])
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_on_notes_list(self):
        response = self.auth_client.get(self.list_url)
        self.assertIn(self.note, response.context['object_list'])

    def test_user_cant_see_notes_of_other_user(self):
        response = self.auth_client.get(self.list_url)
        self.assertNotIn(self.reader_list, response.context['object_list'])
        # self.client.force_login(self.reader)
        # response = self.client.get(self.list_url)
        # self.assertNotIn(self.note, response.context['object_list'])
