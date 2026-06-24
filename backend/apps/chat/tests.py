from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.notebooks.models import Notebook

from .models import Conversation, Message, MessageRole
from .views import AI_FAILURE_MESSAGE


class ConversationSendMessageTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='chat-user',
            email='chat@example.com',
            password='test-password',
        )
        self.notebook = Notebook.objects.create(
            user=self.user,
            name='Chat notebook',
        )
        self.conversation = Conversation.objects.create(
            notebook=self.notebook,
            title='Failure path',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @patch('apps.chat.views.logger')
    @patch('apps.chat.views.call_deepseek_chat', side_effect=RuntimeError('service down'))
    def test_ai_failure_preserves_user_message_and_returns_assistant_failure(
        self,
        _,
        logger,
    ):
        response = self.client.post(
            f'/api/v1/conversations/{self.conversation.id}/messages/send/',
            {'content': 'Summarize this notebook'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        messages = list(Message.objects.order_by('created_at'))
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].role, MessageRole.USER)
        self.assertEqual(messages[0].content, 'Summarize this notebook')
        self.assertEqual(messages[1].role, MessageRole.ASSISTANT)
        self.assertEqual(messages[1].content, AI_FAILURE_MESSAGE)
        self.assertEqual(messages[1].citations, [])

        self.assertEqual(response.data['user_message']['id'], messages[0].id)
        self.assertEqual(response.data['assistant_message']['id'], messages[1].id)
        logger.exception.assert_called_once()
