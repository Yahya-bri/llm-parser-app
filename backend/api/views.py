from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
import os
import base64
import traceback
import logging
import json  # Add this missing import
from packages.vision_parser import ParserService
from .models import Item, Document, ParsedResult
from .serializers import (
    ItemSerializer, 
    DocumentSerializer, 
    ParsedResultSerializer,
    DocumentUploadSerializer,
    DocumentParseSerializer
)

# Set up logger
logger = logging.getLogger(__name__)

@extend_schema(
    description="API root endpoint providing basic information",
    responses={200: {'type': 'object', 'properties': {
        'message': {'type': 'string'},
        'status': {'type': 'string'}
    }}},
    examples=[
        OpenApiExample(
            'Example response',
            value={'message': 'Welcome to the API', 'status': 'API is working correctly'},
            response_only=True
        )
    ]
)
@api_view(['GET'])
def api_root(request):
    """
    API root endpoint providing basic information about the API.
    """
    return Response({
        'message': 'Welcome to the API',
        'status': 'API is working correctly',
    })


# Add a CSRF token endpoint
@api_view(['GET'])
@permission_classes([])  # Allow any - no authentication required
def csrf_token(request):
    """
    Get a CSRF token for the client.
    This view doesn't need to return anything special - just accessing it
    will set the CSRF cookie that the client can then use.
    """
    return Response({"detail": "CSRF cookie set"})


@extend_schema(tags=["Items"])
class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows items to be viewed, created, updated or deleted.
    
    * Requires authentication.
    * Lists all items in the system.
    * Supports filtering, searching, and pagination.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Documents"])
class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for document management.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    authentication_classes = [BasicAuthentication]  # Explicitly set authentication class
    
    @extend_schema(
        request=DocumentUploadSerializer,
        responses={201: DocumentSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Upload a new document."""
        # Add explicit authentication check
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided or are invalid."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        try:
            serializer = DocumentUploadSerializer(data=request.data)
            if serializer.is_valid():
                file = serializer.validated_data['file']
                name = serializer.validated_data.get('name', file.name)
                schema_type = serializer.validated_data.get('schema_type', 'resume')
                
                # Log useful information
                logger.info(f"Uploading document: {name}, type: {schema_type}, size: {file.size} bytes")
                
                # Ensure media directory exists
                media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'documents')
                os.makedirs(media_dir, exist_ok=True)
                
                document = Document.objects.create(
                    file=file,
                    name=name,
                    schema_type=schema_type
                )
                
                return Response(
                    DocumentSerializer(document).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the full stack trace for debugging
            logger.error(f"Error uploading document: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"detail": f"An error occurred while uploading the document: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @extend_schema(
        methods=['POST'],
        request=DocumentParseSerializer,
        responses={200: ParsedResultSerializer}
    )
    @action(detail=False, methods=['post'], url_path='parse')
    def parse_document(self, request):
        """Parse a document using the vision parser."""
        # Log request content type for debugging
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request data: {request.data}")
        
        # Better content type handling
        if request.content_type == 'application/json':
            data = request.data
        elif hasattr(request, 'body') and request.body:
            # Try to parse the raw body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return Response(
                    {"error": f"Invalid JSON format: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Try to use the data directly
            data = request.data
            
        # Validate with serializer
        serializer = DocumentParseSerializer(data=data)
        if serializer.is_valid():
            document_id = serializer.validated_data['document_id']
            page_number = serializer.validated_data.get('page_number', 1)
            schema_type = serializer.validated_data.get('schema_type', None)
            
            try:
                # Check for Google API key
                google_api_key = os.environ.get('GOOGLE_API_KEY')
                if not google_api_key:
                    return Response(
                        {"error": "Google API key is not configured. Please set the GOOGLE_API_KEY environment variable."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                
                if google_api_key == 'your-google-api-key' or google_api_key == 'your-google-api-key-here':
                    return Response(
                        {"error": "Invalid Google API key. Please provide a valid API key in GOOGLE_API_KEY environment variable."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                
                document = Document.objects.get(id=document_id)
                if not schema_type:
                    schema_type = document.schema_type
                
                # Check if result already exists
                existing_result = ParsedResult.objects.filter(
                    document=document,
                    page_number=page_number
                ).first()
                
                if existing_result:
                    return Response(
                        ParsedResultSerializer(existing_result).data,
                        status=status.HTTP_200_OK
                    )
                
                # Initialize parser service
                parser_service = ParserService(
                    schema_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schemas'),
                    default_schema=schema_type
                )
                
                # Parse the document
                result = parser_service.parse_document(
                    document_path=document.file.path,
                    schema_type=schema_type,
                    page_number=page_number
                )
                
                # Save the result
                parsed_result = ParsedResult.objects.create(
                    document=document,
                    page_number=page_number,
                    result_data=result
                )
                
                return Response(
                    ParsedResultSerializer(parsed_result).data,
                    status=status.HTTP_200_OK
                )
                
            except Document.DoesNotExist:
                return Response(
                    {"error": "Document not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                # Handle Google API key errors specifically
                error_str = str(e)
                logger.error(f"Error parsing document: {error_str}")
                logger.error(traceback.format_exc())
                
                if 'API key not valid' in error_str or 'INVALID_ARGUMENT' in error_str:
                    return Response(
                        {"error": "Google API key is invalid. Please check your GOOGLE_API_KEY environment variable."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        responses={200: {'type': 'object', 'properties': {
            'page_count': {'type': 'integer'},
            'preview': {'type': 'string'}
        }}}
    )
    @action(detail=True, methods=['get'], url_path='preview/(?P<page>[0-9]+)')
    def preview(self, request, pk=None, page=1):
        """Get a preview image of a document page."""
        try:
            document = self.get_object()
            page = int(page)
            
            # Get document file path
            file_path = document.file.path
            
            # Check file extension
            _, ext = os.path.splitext(file_path.lower())
            
            # For PDFs, use the utility to get specific page
            if ext == '.pdf':
                from packages.vision_parser.utils import pdf_page_to_base64
                preview_data = pdf_page_to_base64(file_path, page)
                
                # Also get page count
                import fitz
                pdf_document = fitz.open(file_path)
                page_count = len(pdf_document)
                pdf_document.close()
                
            # For images, just return the image
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                from packages.vision_parser.utils import image_to_base64
                preview_data = image_to_base64(file_path)
                page_count = 1
            else:
                return Response(
                    {"error": "Unsupported file format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            return Response({
                'page_count': page_count,
                'preview': preview_data
            })
            
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(tags=["Parsed Results"])
class ParsedResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing parsed results.
    """
    queryset = ParsedResult.objects.all()
    serializer_class = ParsedResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter results by document if specified."""
        queryset = super().get_queryset()
        document_id = self.request.query_params.get('document_id', None)
        if document_id is not None:
            queryset = queryset.filter(document_id=document_id)
        return queryset
