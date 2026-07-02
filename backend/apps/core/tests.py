from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class HealthCheckTests(TestCase):
    def test_health_endpoint_is_public_and_returns_ok(self):
        client = APIClient()

        response = client.get('/api/v1/health/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')


class ApiRendererTests(TestCase):
    def test_successful_response_is_wrapped_in_code_message_data(self):
        user = User.objects.create_user(
            username='rendereruser',
            email='renderer@example.com',
            password='rendererpass1',
        )
        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/v1/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['code'], 200)
        self.assertEqual(response.json()['message'], 'success')
        self.assertEqual(response.json()['data']['username'], 'rendereruser')

    def test_no_content_response_has_empty_body(self):
        user = User.objects.create_user(
            username='nocontentuser',
            email='nocontent@example.com',
            password='nocontentpass1',
        )
        client = APIClient()
        client.force_authenticate(user)

        response = client.post('/api/v1/auth/logout/', {})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')


class ApiExceptionHandlerTests(TestCase):
    def test_validation_error_is_wrapped_with_field_errors(self):
        client = APIClient()

        response = client.post('/api/v1/auth/register/', {
            'username': '',
            'email': 'not-an-email',
            'password': '123',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertEqual(body['code'], status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(body['data'])
        self.assertTrue(body['errors'])

    def test_authentication_error_is_wrapped_with_detail_message(self):
        client = APIClient()

        response = client.get('/api/v1/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response.json()
        self.assertEqual(body['code'], status.HTTP_401_UNAUTHORIZED)
        self.assertIsNone(body['data'])
        self.assertIsInstance(body['message'], str)

    def test_not_found_error_is_wrapped(self):
        user = User.objects.create_user(
            username='notfounduser',
            email='notfound@example.com',
            password='notfoundpass1',
        )
        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/v1/notebooks/999999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        body = response.json()
        self.assertEqual(body['code'], status.HTTP_404_NOT_FOUND)
        self.assertIsNone(body['data'])
