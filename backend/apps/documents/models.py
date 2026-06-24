from django.db import models

from apps.notebooks.models import Notebook


class DocumentStatus(models.TextChoices):
    UPLOADING = 'uploading', '上传中'
    PARSING = 'parsing', '解析中'
    COMPLETED = 'completed', '完成'
    FAILED = 'failed', '失败'


class Document(models.Model):
    notebook = models.ForeignKey(
        Notebook,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.UPLOADING,
    )
    chunk_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notebook', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks',
    )
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']
        indexes = [
            models.Index(fields=['document', 'position']),
        ]

    def __str__(self):
        return f'{self.document_id}#{self.position}'
