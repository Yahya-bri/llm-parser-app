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
    schema_type = models.CharField(max_length=50, choices=SCHEMA_CHOICES, default='resume')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class ParsedResult(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='parsed_results')
    page_number = models.PositiveIntegerField(default=1)
    result_data = models.JSONField()
    parsed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('document', 'page_number')
        
    def __str__(self):
        return f"{self.document.name} - Page {self.page_number}"
