from rest_framework import serializers

from .models import Document, DocumentAsset


class DocumentSerializer(serializers.ModelSerializer):
    asset_count = serializers.SerializerMethodField()
    parse_overview = serializers.SerializerMethodField()
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
            'parse_overview',
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

    # NOTE: all asset-derived fields below iterate `obj.assets.all()` in Python
    # rather than issuing per-field `.filter().count()` queries, so that a
    # `prefetch_related('assets')` at the view level (see views.py) turns this
    # from ~12 queries per document into a single query for the whole page.

    def _assets(self, obj):
        return list(obj.assets.all())

    def get_asset_count(self, obj):
        return len(self._assets(obj))

    def get_parse_overview(self, obj):
        source_counts: dict[str, int] = {}
        parser_versions: list[int] = []
        pages: set[int] = set()

        for chunk in obj.chunks.all():
            metadata = chunk.metadata or {}
            source_type = metadata.get('source_type') or 'text'
            source_counts[source_type] = source_counts.get(source_type, 0) + 1

            parser_version = metadata.get('parser_version')
            if isinstance(parser_version, int) and parser_version not in parser_versions:
                parser_versions.append(parser_version)

            page = metadata.get('page')
            if isinstance(page, int):
                pages.add(page)

        sorted_pages = sorted(pages)
        return {
            'chunk_count': obj.chunk_count,
            'asset_count': len(self._assets(obj)),
            'source_counts': source_counts,
            'page_start': sorted_pages[0] if sorted_pages else None,
            'page_end': sorted_pages[-1] if sorted_pages else None,
            'page_count': len(sorted_pages),
            'parser_versions': parser_versions,
        }

    def get_ocr_count(self, obj):
        return sum(1 for asset in self._assets(obj) if asset.ocr_status == DocumentAsset.OCRStatus.SUCCESS)

    def get_ocr_pending_count(self, obj):
        return sum(1 for asset in self._assets(obj) if asset.ocr_status == DocumentAsset.OCRStatus.PENDING)

    def get_ocr_failed_count(self, obj):
        return sum(1 for asset in self._assets(obj) if asset.ocr_status == DocumentAsset.OCRStatus.FAILED)

    def get_ocr_skipped_count(self, obj):
        return sum(1 for asset in self._assets(obj) if asset.ocr_status == DocumentAsset.OCRStatus.SKIPPED)

    def get_ocr_error_message(self, obj):
        candidates = sorted(
            (asset for asset in self._assets(obj) if asset.ocr_error),
            key=lambda asset: asset.position,
        )
        return candidates[0].ocr_error if candidates else ''

    def get_vision_count(self, obj):
        return sum(1 for asset in self._assets(obj) if asset.vision_status == DocumentAsset.VisionStatus.SUCCESS)

    def get_vision_pending_count(self, obj):
        return sum(1 for asset in self._assets(obj) if asset.vision_status == DocumentAsset.VisionStatus.PENDING)

    def get_vision_failed_count(self, obj):
        return sum(1 for asset in self._assets(obj) if asset.vision_status == DocumentAsset.VisionStatus.FAILED)

    def get_vision_skipped_count(self, obj):
        return sum(1 for asset in self._assets(obj) if asset.vision_status == DocumentAsset.VisionStatus.SKIPPED)

    def get_vision_error_message(self, obj):
        candidates = sorted(
            (asset for asset in self._assets(obj) if asset.vision_error),
            key=lambda asset: asset.position,
        )
        return candidates[0].vision_error if candidates else ''


class DocumentUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        write_only=True,
    )
