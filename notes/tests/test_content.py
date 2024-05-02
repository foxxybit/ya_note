from django.contrib.auth import get_user_model
from django.urls import reverse

from .mixins import NoteMixin, ReaderMixin
from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestFormAndListPages(NoteMixin, ReaderMixin):

    @classmethod
    def setUpTestData(cls):
        ReaderMixin.setUpTestData()
        NoteMixin.setUpTestData()
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
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_on_notes_list(self):
        response = self.author_client.get(self.list_url)
        self.assertIn(self.note, response.context['object_list'])

    def test_user_cant_see_notes_of_other_user(self):
        response = self.author_client.get(self.list_url)
        self.assertNotIn(self.reader_list, response.context['object_list'])
