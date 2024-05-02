from http import HTTPStatus
from pytils.translit import slugify

from django.urls import reverse

from .mixins import NoteMixin, ReaderLoginMixin
from notes.forms import WARNING
from notes.models import Note


NOTE_TITLE = 'Заголовок'
NOTE_TEXT = 'Текст заметки'
NEW_NOTE_TEXT = 'Обновленная заметка'
NOTE_SLUG = 'test'


class TestNoteCreation(ReaderLoginMixin):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        ReaderLoginMixin.setUpTestData()
        cls.form_data = {
            'title': NOTE_TEXT,
            'text': NOTE_TEXT,
            'slug': NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.reader_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, NOTE_TEXT)
        self.assertEqual(note.title, NOTE_TEXT)
        self.assertEqual(note.slug, NOTE_SLUG)
        self.assertEqual(note.author, self.reader)

    def user_cant_create_not_unique_slug(self):
        note = Note.objects.create(
            title=NOTE_TEXT,
            text=NOTE_TEXT,
            author=self.reader
        )
        self.form_data['slug'] = note.slug
        response = self.reader_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.form_data['slug'] + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.reader_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(NoteMixin, ReaderLoginMixin):

    @classmethod
    def setUpTestData(cls):
        NoteMixin.setUpTestData()
        ReaderLoginMixin.setUpTestData()
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=[cls.note.slug])
        cls.delete_url = reverse('notes:delete', args=[cls.note.slug])
        cls.form_data = {'title': NOTE_TEXT, 'text': NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, NOTE_TEXT)
