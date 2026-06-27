from rest_framework import serializers

from .models import Document, DocumentAsset


class DocumentSerializer(serializers.ModelSerializer):
    asset_count = serializers.SerializerMethodField()
    ocr_count = serializers.SerializerMethodField()
    ocr_pending_count = serializers.SerializerMethodField()
    ocr_failed_count = serializers.SerializerMethodField()
    ocr_skipped_count = serializers.SerializerMethodField()
    ocr_error_message = serializers.SerializerMethodField()
    vision_count = serializers.SerializerMethodField()
    vision_pending_count = serializers.SerializerMethodField()
    vision_failed_count = serializers.SerializerMethodField()
    vision_skipped_count = serializers.SerializerMethodField()
    vision_error_message = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id',
            'notebook_id',
            'name',
            'file_type',
            'file_size',
            'status',
            'chunk_count',
            'asset_count',
            'ocr_count',
            'ocr_pending_count',
            'ocr_failed_count',
            'ocr_skipped_count',
            'ocr_error_message',
            'vision_count',
            'vision_pending_count',
            'vision_failed_count',
            'vision_skipped_count',
            'vision_error_message',
            'error_message',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields

    def get_asset_count(self, obj):
        return obj.assets.count()

    def get_ocr_count(self, obj):
        return obj.assets.filter(ocr_status=DocumentAsset.OCRStatus.SUCCESS).count()

    def get_ocr_pending_count(self, obj):
        return obj.assets.filter(ocr_status=DocumentAsset.OCRStatus.PENDING).count()

    def get_ocr_failed_count(self, obj):
        return obj.assets.filter(ocr_status=DocumentAsset.OCRStatus.FAILED).count()

    def get_ocr_skipped_count(self, obj):
        return obj.assets.filter(ocr_status=DocumentAsset.OCRStatus.SKIPPED).count()

    def get_ocr_error_message(self, obj):
        asset = obj.assets.exclude(ocr_error='').order_by('position').first()
        return asset.ocr_error if asset else ''

    def get_vision_count(self, obj):
        return obj.assets.filter(vision_status=DocumentAsset.VisionStatus.SUCCESS).count()

    def get_vision_pending_count(self, obj):
        return obj.assets.filter(vision_status=DocumentAsset.VisionStatus.PENDING).count()

    def get_vision_failed_count(self, obj):
        return obj.assets.filter(vision_status=DocumentAsset.VisionStatus.FAILED).count()

    def get_vision_skipped_count(self, obj):
        return obj.assets.filter(vision_status=DocumentAsset.VisionStatus.SKIPPED).count()

    def get_vision_error_message(self, obj):
        asset = obj.assets.exclude(vision_error='').order_by('position').first()
        return asset.vision_error if asset else ''


class DocumentUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        write_only=True,
    )
