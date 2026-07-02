from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

User = get_user_model()


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user_and_returns_tokens(self):
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'strongpass123',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('strongpass123'))

    def test_register_rejects_duplicate_username_case_insensitive(self):
        User.objects.create_user(username='taken', email='a@example.com', password='pass12345')

        response = self.client.post('/api/v1/auth/register/', {
            'username': 'TAKEN',
            'email': 'b@example.com',
            'password': 'pass12345',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_register_rejects_duplicate_email_case_insensitive(self):
        User.objects.create_user(username='first', email='dup@example.com', password='pass12345')

        response = self.client.post('/api/v1/auth/register/', {
            'username': 'second',
            'email': 'DUP@example.com',
            'password': 'pass12345',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_register_rejects_password_too_short(self):
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'shortpw',
            'email': 'shortpw@example.com',
            'password': '123',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='shortpw').exists())

    def test_register_rejects_common_password(self):
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'commonpw',
            'email': 'commonpw@example.com',
            'password': 'password',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='commonpw').exists())

    def test_register_missing_fields_returns_400(self):
        response = self.client.post('/api/v1/auth/register/', {'username': 'onlyusername'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='correctpass1',
        )

    def test_login_with_correct_credentials_returns_tokens(self):
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'loginuser',
            'password': 'correctpass1',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_wrong_password_returns_401(self):
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'loginuser',
            'password': 'wrongpass',
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_unknown_username_returns_401(self):
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'nosuchuser',
            'password': 'whatever123',
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RefreshViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='refreshuser',
            email='refresh@example.com',
            password='refreshpass1',
        )

    def test_refresh_with_valid_token_returns_new_access_token(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post('/api/v1/auth/refresh/', {'refresh': str(refresh)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_with_invalid_token_returns_401(self):
        response = self.client.post('/api/v1/auth/refresh/', {'refresh': 'not-a-valid-token'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_with_blacklisted_token_returns_401(self):
        refresh = RefreshToken.for_user(self.user)
        refresh.blacklist()

        response = self.client.post('/api/v1/auth/refresh/', {'refresh': str(refresh)})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='logoutuser',
            email='logout@example.com',
            password='logoutpass1',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_logout_blacklists_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post('/api/v1/auth/logout/', {'refresh': str(refresh)})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        outstanding = OutstandingToken.objects.get(jti=refresh['jti'])
        self.assertTrue(BlacklistedToken.objects.filter(token=outstanding).exists())

    def test_logout_with_invalid_token_still_returns_204(self):
        response = self.client.post('/api/v1/auth/logout/', {'refresh': 'garbage-token'})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_without_token_returns_204(self):
        response = self.client.post('/api/v1/auth/logout/', {})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_requires_authentication(self):
        anonymous_client = APIClient()

        response = anonymous_client.post('/api/v1/auth/logout/', {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='meuser',
            email='me@example.com',
            password='mepass123',
        )

    def test_me_returns_authenticated_user_profile(self):
        client = APIClient()
        client.force_authenticate(self.user)

        response = client.get('/api/v1/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'meuser')
        self.assertEqual(response.data['email'], 'me@example.com')
        self.assertNotIn('password', response.data)

    def test_me_requires_authentication(self):
        client = APIClient()

        response = client.get('/api/v1/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
