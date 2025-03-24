from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, DocumentViewSet, ParsedResultViewSet, api_root, csrf_token

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'parsed-results', ParsedResultViewSet)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('csrf/', csrf_token, name='csrf'),
    # Add explicit path for document parsing to avoid routing issues
    path('documents/parse/', DocumentViewSet.as_view({'post': 'parse_document'}), name='document-parse'),
]
