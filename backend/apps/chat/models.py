from django.db import models

from apps.notebooks.models import Notebook


class Conversation(models.Model):
    notebook = models.ForeignKey(
        Notebook,
        on_delete=models.CASCADE,
        related_name='conversations',
    )
    title = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['notebook', '-updated_at']),
        ]

    def __str__(self) -> str:
        return self.title or f'Conversation {self.pk}'


class MessageRole(models.TextChoices):
    USER = 'user', '用户'
    ASSISTANT = 'assistant', '助手'


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=20, choices=MessageRole.choices)
    content = models.TextField()
    citations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self) -> str:
        return f'{self.role}: {self.content[:30]}'

