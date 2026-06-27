from django.urls import path

from . import views

urlpatterns = [
    path(
        'notebooks/<int:notebook_pk>/documents/',
        views.NotebookDocumentListCreateView.as_view(),
        name='notebook-documents',
    ),
    path(
        'documents/<int:pk>/',
        views.DocumentDetailView.as_view(),
        name='document-detail',
    ),
    path(
        'documents/<int:pk>/reparse/',
        views.DocumentReparseView.as_view(),
        name='document-reparse',
    ),
]
