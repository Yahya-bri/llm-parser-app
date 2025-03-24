import os
import json
from typing import Dict, Any, Optional, Union

from .parser import DocumentParser
from .utils import get_document_as_base64


class ParserService:
    """Service wrapper for document parsing."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        schema_dir: Optional[str] = None,
        schemas: Optional[Dict[str, Dict[str, Any]]] = None,
        default_schema: str = "resume",
        model: str = "gemini-2.0-flash"
    ):
        """Initialize the parser service.
        
        Args:
            api_key: Google API key
            schema_dir: Directory containing schema JSON files
            schemas: Direct schema dictionaries (alternative to schema_dir)
            default_schema: Default schema type to use
            model: Model to use for parsing
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        
        # Load schemas
        self.schemas = {}
        if schemas:
            self.schemas = schemas
        elif schema_dir:
            for file in os.listdir(schema_dir):
                if file.endswith(".json"):
                    schema_name = os.path.splitext(file)[0]
                    with open(os.path.join(schema_dir, file), "r") as f:
                        self.schemas[schema_name] = json.load(f)
        else:
            raise ValueError("Either schemas or schema_dir must be provided")
            
        self.default_schema = default_schema
        if default_schema not in self.schemas:
            raise ValueError(f"Default schema '{default_schema}' not found in available schemas")
            
        self.model = model
        self.parsers = {}
        
    def _get_parser(self, schema_type: str) -> DocumentParser:
        """Get or create a parser for the given schema type."""
        if schema_type not in self.schemas:
            raise ValueError(f"Schema '{schema_type}' not found in available schemas")
            
        if schema_type not in self.parsers:
            self.parsers[schema_type] = DocumentParser(
                api_key=self.api_key,
                schema=self.schemas[schema_type],
                model=self.model
            )
            
        return self.parsers[schema_type]
        
    def parse_document(
        self, 
        document_path: str, 
        schema_type: Optional[str] = None,
        page_number: int = 1,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Parse a document using the specified schema.
        
        Args:
            document_path: Path to the document
            schema_type: Schema type to use (default uses the default_schema)
            page_number: Page number for PDFs
            prompt: Custom prompt (optional)
            
        Returns:
            Structured data based on the schema
        """
        schema_type = schema_type or self.default_schema
        parser = self._get_parser(schema_type)
        
        if prompt:
            return parser.parse_document(document_path, page_number, prompt)
        else:
            return parser.parse_document(document_path, page_number)
            
    def parse_base64(
        self, 
        base64_image: str,
        schema_type: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Parse a base64-encoded image using the specified schema.
        
        Args:
            base64_image: Base64-encoded image
            schema_type: Schema type to use (default uses the default_schema)
            prompt: Custom prompt (optional)
            
        Returns:
            Structured data based on the schema
        """
        schema_type = schema_type or self.default_schema
        parser = self._get_parser(schema_type)
        
        if prompt:
            return parser.parse_base64(base64_image, prompt)
        else:
            return parser.parse_base64(base64_image)
