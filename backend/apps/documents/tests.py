from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.notebooks.models import Notebook

from .models import Document, DocumentStatus


class DocumentUploadTests(TransactionTestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.settings_override = override_settings(
            MEDIA_ROOT=Path(self.temp_dir.name),
            MAX_UPLOAD_SIZE_MB=20,
        )
        self.settings_override.enable()

        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='upload-user',
            email='upload@example.com',
            password='test-password',
        )
        self.notebook = Notebook.objects.create(
            user=self.user,
            name='Upload notebook',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.settings_override.disable()
        self.temp_dir.cleanup()

    def test_rejects_mixed_invalid_upload_before_saving_any_file(self):
        valid_file = self._file('valid.txt', b'valid content')
        invalid_file = self._file('slides.pptx', b'not supported')

        with patch('apps.documents.views.save_uploaded_file') as save_uploaded_file:
            response = self.client.post(
                f'/api/v1/notebooks/{self.notebook.id}/documents/',
                {'files': [valid_file, invalid_file]},
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(save_uploaded_file.called)
        self.assertEqual(Document.objects.count(), 0)

    def test_valid_upload_creates_document_and_enqueues_parse_after_commit(self):
        uploaded_file = self._file('notes.md', b'# Notes\n\nBatch upload test.')

        with patch('apps.documents.views.enqueue_parse_task') as enqueue_parse_task:
            response = self.client.post(
                f'/api/v1/notebooks/{self.notebook.id}/documents/',
                {'files': [uploaded_file]},
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        document = Document.objects.get()
        self.assertEqual(document.name, 'notes.md')
        self.assertEqual(document.file_type, 'md')
        self.assertEqual(document.status, DocumentStatus.UPLOADING)
        self.assertTrue((Path(self.temp_dir.name) / document.file_path).exists())
        enqueue_parse_task.assert_called_once_with(document.id)

    @staticmethod
    def _file(name: str, content: bytes):
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile(name, content)
