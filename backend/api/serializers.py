from rest_framework import serializers
from .models import Item, Document, ParsedResult


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file', 'name', 'schema_type', 'uploaded_at']


class ParsedResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedResult
        fields = ['id', 'document', 'page_number', 'result_data', 'parsed_at']
        

class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    name = serializers.CharField(max_length=255, required=False)
    schema_type = serializers.ChoiceField(choices=Document.SCHEMA_CHOICES, default='resume')


class DocumentParseSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    page_number = serializers.IntegerField(default=1)
    schema_type = serializers.ChoiceField(choices=Document.SCHEMA_CHOICES, required=False)
