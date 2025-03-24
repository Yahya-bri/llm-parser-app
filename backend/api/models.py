from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Document(models.Model):
    SCHEMA_CHOICES = [
        ('resume', 'Resume'),
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('id_card', 'ID Card')
    ]
    
    file = models.FileField(upload_to='documents/')
    name = models.CharField(max_length=255)
    schema_type = models.CharField(max_length=100, default='resume')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Check if schema_type is one of the built-in choices
        built_in_schemas = dict(self.SCHEMA_CHOICES).keys()
        if self.schema_type not in built_in_schemas:
            # Validate that it's a valid custom schema
            try:
                Schema.objects.get(name=self.schema_type)
            except Schema.DoesNotExist:
                # Fall back to default schema if the specified one doesn't exist
                self.schema_type = 'resume'
        super().save(*args, **kwargs)


class ParsedResult(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='parsed_results')
    page_number = models.PositiveIntegerField(default=1)
    result_data = models.JSONField()
    parsed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('document', 'page_number')
        
    def __str__(self):
        return f"{self.document.name} - Page {self.page_number}"


class Schema(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    schema_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
