from rest_framework import serializers

from .models import Conversation, Message
from . import search_modes


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id', 'notebook_id', 'title', 'created_at', 'updated_at')
        read_only_fields = fields


class ConversationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('title',)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'conversation_id', 'role', 'content', 'citations', 'created_at')
        read_only_fields = fields


class SendMessageSerializer(serializers.Serializer):
    SEARCH_MODE_LOCAL = search_modes.SEARCH_MODE_LOCAL
    SEARCH_MODE_WEB = search_modes.SEARCH_MODE_WEB
    SEARCH_MODE_HYBRID = search_modes.SEARCH_MODE_HYBRID
    SEARCH_MODE_CHOICES = search_modes.SEARCH_MODE_CHOICES

    content = serializers.CharField(allow_blank=False, trim_whitespace=True)
    web_search = serializers.BooleanField(required=False, default=False)
    search_mode = serializers.ChoiceField(
        choices=SEARCH_MODE_CHOICES,
        required=False,
        default=SEARCH_MODE_LOCAL,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['search_mode'] = search_modes.normalize_search_mode(
            attrs.get('search_mode'),
            web_search=attrs.get('web_search', False),
        )
        return attrs

