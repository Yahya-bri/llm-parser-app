from rest_framework import serializers
from .models import Item, Document, ParsedResult, Schema


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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get built-in schema choices
        choices = dict(Document.SCHEMA_CHOICES)
        
        # Add custom schemas from database
        try:
            custom_schemas = Schema.objects.all()
            for schema in custom_schemas:
                choices[schema.name] = schema.name
        except:
            # Handle case when database is not yet set up (migrations running)
            pass
            
        self.fields['schema_type'] = serializers.ChoiceField(
            choices=[(k, v) for k, v in choices.items()],
            default='resume'
        )


class DocumentParseSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    page_number = serializers.IntegerField(default=1)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get built-in schema choices
        choices = dict(Document.SCHEMA_CHOICES)
        
        # Add custom schemas from database
        try:
            custom_schemas = Schema.objects.all()
            for schema in custom_schemas:
                choices[schema.name] = schema.name
        except:
            # Handle case when database is not yet set up (migrations running)
            pass
            
        self.fields['schema_type'] = serializers.ChoiceField(
            choices=[(k, v) for k, v in choices.items()],
            required=False
        )


class SchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schema
        fields = ['id', 'name', 'description', 'schema_json', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_schema_json(self, value):
        """
        Validate that the schema JSON is properly formatted.
        """
        # Basic validation to ensure it has required fields
        required_fields = ['title', 'description', 'type', 'properties']
        
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Schema JSON must include '{field}' field")
                
        # Ensure it's an object type
        if value.get('type') != 'object':
            raise serializers.ValidationError("Schema root type must be 'object'")
            
        # Ensure properties is a dictionary
        if not isinstance(value.get('properties'), dict):
            raise serializers.ValidationError("'properties' must be an object")
            
        return value
