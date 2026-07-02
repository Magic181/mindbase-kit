from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.documents.models import Document, DocumentStatus

from .models import Notebook

User = get_user_model()


class NotebookListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='ownerpass1',
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='otherpass1',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_only_returns_own_notebooks(self):
        Notebook.objects.create(user=self.user, name='Mine')
        Notebook.objects.create(user=self.other_user, name='Not mine')

        response = self.client.get('/api/v1/notebooks/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data['items']]
        self.assertEqual(names, ['Mine'])
        self.assertEqual(response.data['total'], 1)

    def test_list_requires_authentication(self):
        anonymous_client = APIClient()

        response = anonymous_client.get('/api/v1/notebooks/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_filters_by_name_or_description(self):
        Notebook.objects.create(user=self.user, name='Machine Learning', description='')
        Notebook.objects.create(user=self.user, name='Cooking', description='recipes about pasta')
        Notebook.objects.create(user=self.user, name='Travel', description='')

        response = self.client.get('/api/v1/notebooks/', {'search': 'pasta'})

        names = [item['name'] for item in response.data['items']]
        self.assertEqual(names, ['Cooking'])

    def test_favorite_filter_only_returns_favorited_notebooks(self):
        Notebook.objects.create(user=self.user, name='Favorited', is_favorite=True)
        Notebook.objects.create(user=self.user, name='Not favorited', is_favorite=False)

        response = self.client.get('/api/v1/notebooks/', {'is_favorite': 'true'})

        names = [item['name'] for item in response.data['items']]
        self.assertEqual(names, ['Favorited'])

    def test_ordering_rejects_unknown_field_and_falls_back_to_default(self):
        first = Notebook.objects.create(user=self.user, name='A')
        second = Notebook.objects.create(user=self.user, name='B')
        # auto_now can collapse to the same timestamp as `first` on fast test runs;
        # set updated_at explicitly (bypassing auto_now) so the default ordering is unambiguous.
        Notebook.objects.filter(id=first.id).update(updated_at=first.updated_at)
        Notebook.objects.filter(id=second.id).update(
            updated_at=first.updated_at + timedelta(seconds=1),
        )

        response = self.client.get('/api/v1/notebooks/', {'ordering': 'DROP TABLE notebooks'})

        ids = [item['id'] for item in response.data['items']]
        self.assertEqual(ids, [second.id, first.id])

    def test_document_count_reflects_related_documents(self):
        notebook = Notebook.objects.create(user=self.user, name='With docs')
        Document.objects.create(
            notebook=notebook,
            name='a.txt',
            file_path='files/a.txt',
            file_type='txt',
            status=DocumentStatus.COMPLETED,
        )
        Document.objects.create(
            notebook=notebook,
            name='b.txt',
            file_path='files/b.txt',
            file_type='txt',
            status=DocumentStatus.COMPLETED,
        )

        response = self.client.get('/api/v1/notebooks/')

        self.assertEqual(response.data['items'][0]['document_count'], 2)


class NotebookCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass1',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_assigns_current_user_as_owner(self):
        response = self.client.post('/api/v1/notebooks/', {
            'name': 'New notebook',
            'description': 'a description',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notebook = Notebook.objects.get(name='New notebook')
        self.assertEqual(notebook.user, self.user)
        self.assertEqual(response.data['name'], 'New notebook')

    def test_create_rejects_blank_name(self):
        response = self.client.post('/api/v1/notebooks/', {
            'name': '   ',
            'description': '',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Notebook.objects.count(), 0)

    def test_create_strips_whitespace_from_name(self):
        response = self.client.post('/api/v1/notebooks/', {
            'name': '  Padded name  ',
            'description': '',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Padded name')

    def test_create_response_ignores_client_supplied_favorite_flag(self):
        response = self.client.post('/api/v1/notebooks/', {
            'name': 'Sneaky',
            'description': '',
            'is_favorite': True,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notebook = Notebook.objects.get(name='Sneaky')
        self.assertFalse(notebook.is_favorite)


class NotebookDetailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='detailowner',
            email='detailowner@example.com',
            password='detailpass1',
        )
        self.other_user = User.objects.create_user(
            username='detailother',
            email='detailother@example.com',
            password='detailpass2',
        )
        self.notebook = Notebook.objects.create(user=self.user, name='Detail notebook')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_own_notebook(self):
        response = self.client.get(f'/api/v1/notebooks/{self.notebook.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.notebook.id)

    def test_retrieve_other_users_notebook_returns_404(self):
        other_client = APIClient()
        other_client.force_authenticate(self.other_user)

        response = other_client.get(f'/api/v1/notebooks/{self.notebook.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_own_notebook(self):
        response = self.client.patch(f'/api/v1/notebooks/{self.notebook.id}/', {
            'name': 'Renamed',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notebook.refresh_from_db()
        self.assertEqual(self.notebook.name, 'Renamed')

    def test_update_rejects_blank_name(self):
        response = self.client.patch(f'/api/v1/notebooks/{self.notebook.id}/', {
            'name': '   ',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.notebook.refresh_from_db()
        self.assertEqual(self.notebook.name, 'Detail notebook')

    def test_update_other_users_notebook_returns_404(self):
        other_client = APIClient()
        other_client.force_authenticate(self.other_user)

        response = other_client.patch(f'/api/v1/notebooks/{self.notebook.id}/', {
            'name': 'Hijacked',
        })

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.notebook.refresh_from_db()
        self.assertEqual(self.notebook.name, 'Detail notebook')

    def test_delete_own_notebook(self):
        response = self.client.delete(f'/api/v1/notebooks/{self.notebook.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notebook.objects.filter(id=self.notebook.id).exists())

    def test_delete_other_users_notebook_returns_404(self):
        other_client = APIClient()
        other_client.force_authenticate(self.other_user)

        response = other_client.delete(f'/api/v1/notebooks/{self.notebook.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Notebook.objects.filter(id=self.notebook.id).exists())

    def test_delete_cascades_to_documents(self):
        Document.objects.create(
            notebook=self.notebook,
            name='a.txt',
            file_path='files/a.txt',
            file_type='txt',
            status=DocumentStatus.COMPLETED,
        )

        response = self.client.delete(f'/api/v1/notebooks/{self.notebook.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Document.objects.count(), 0)


class NotebookFavoriteActionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='favuser',
            email='favuser@example.com',
            password='favpass123',
        )
        self.other_user = User.objects.create_user(
            username='favother',
            email='favother@example.com',
            password='favpass456',
        )
        self.notebook = Notebook.objects.create(user=self.user, name='Fav notebook')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_favorite_toggles_from_false_to_true(self):
        response = self.client.post(f'/api/v1/notebooks/{self.notebook.id}/favorite/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_favorite'])
        self.notebook.refresh_from_db()
        self.assertTrue(self.notebook.is_favorite)

    def test_favorite_toggles_back_to_false_on_second_call(self):
        self.client.post(f'/api/v1/notebooks/{self.notebook.id}/favorite/')
        response = self.client.post(f'/api/v1/notebooks/{self.notebook.id}/favorite/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_favorite'])

    def test_favorite_other_users_notebook_returns_404(self):
        other_client = APIClient()
        other_client.force_authenticate(self.other_user)

        response = other_client.post(f'/api/v1/notebooks/{self.notebook.id}/favorite/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.notebook.refresh_from_db()
        self.assertFalse(self.notebook.is_favorite)


class NotebookPaginationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='pageuser',
            email='pageuser@example.com',
            password='pagepass123',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        for i in range(25):
            Notebook.objects.create(user=self.user, name=f'Notebook {i}')

    def test_default_page_size_is_20(self):
        response = self.client.get('/api/v1/notebooks/')

        self.assertEqual(len(response.data['items']), 20)
        self.assertEqual(response.data['total'], 25)
        self.assertEqual(response.data['page'], 1)

    def test_custom_page_size_is_respected_up_to_max(self):
        response = self.client.get('/api/v1/notebooks/', {'page_size': 100})

        self.assertEqual(len(response.data['items']), 25)

    def test_second_page_returns_remaining_items(self):
        response = self.client.get('/api/v1/notebooks/', {'page': 2})

        self.assertEqual(len(response.data['items']), 5)
        self.assertEqual(response.data['page'], 2)
