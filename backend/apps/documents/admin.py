from django.contrib import admin

from .models import Document, DocumentChunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'notebook', 'file_type', 'status', 'chunk_count', 'created_at')
    list_filter = ('status', 'file_type')
    search_fields = ('name',)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'position')
    search_fields = ('content',)
