from pathlib import Path

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notebooks.models import Notebook

from .models import Document, DocumentStatus
from .serializers import DocumentSerializer
from .storage import delete_file, save_uploaded_file
from .tasks import parse_document_task

ALLOWED_EXTENSIONS = {'.txt', '.md', '.markdown', '.pdf', '.docx'}


def normalize_file_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == '.markdown':
        return 'md'
    return ext.lstrip('.')


def get_user_notebook(user, notebook_id: int) -> Notebook:
    try:
        return Notebook.objects.get(pk=notebook_id, user=user)
    except Notebook.DoesNotExist as exc:
        raise NotFound('笔记本不存在') from exc


def get_user_document(user, document_id: int) -> Document:
    try:
        return Document.objects.select_related('notebook').get(
            pk=document_id,
            notebook__user=user,
        )
    except Document.DoesNotExist as exc:
        raise NotFound('文档不存在') from exc


class NotebookDocumentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, notebook_pk: int):
        notebook = get_user_notebook(request.user, notebook_pk)
        documents = notebook.documents.all()
        return Response(DocumentSerializer(documents, many=True).data)

    def post(self, request, notebook_pk: int):
        notebook = get_user_notebook(request.user, notebook_pk)
        files = request.FILES.getlist('files')
        if not files:
            single = request.FILES.get('file')
            files = [single] if single else []

        if not files:
            raise ValidationError({'files': '请选择要上传的文件'})

        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        created = []

        for uploaded in files:
            ext = Path(uploaded.name).suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ValidationError({
                    'files': f'不支持的文件格式: {uploaded.name}（支持 TXT/MD/PDF/DOCX）',
                })
            if uploaded.size > max_size:
                raise ValidationError({
                    'files': f'文件过大: {uploaded.name}（最大 {settings.MAX_UPLOAD_SIZE_MB}MB）',
                })

            file_type = normalize_file_type(uploaded.name)
            relative_path, size = save_uploaded_file(
                request.user.id,
                notebook.id,
                uploaded,
            )
            document = Document.objects.create(
                notebook=notebook,
                name=uploaded.name,
                file_path=relative_path,
                file_size=size,
                file_type=file_type,
                status=DocumentStatus.UPLOADING,
            )
            parse_document_task.delay(document.id)
            created.append(document)

        return Response(
            DocumentSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        document = get_user_document(request.user, pk)
        return Response(DocumentSerializer(document).data)

    def delete(self, request, pk: int):
        document = get_user_document(request.user, pk)
        delete_file(document.file_path)
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
