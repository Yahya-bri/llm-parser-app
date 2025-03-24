from django.contrib import admin
from .models import Item, Document, ParsedResult, Schema

admin.site.register(Item)
admin.site.register(Document)
admin.site.register(ParsedResult)
admin.site.register(Schema)
