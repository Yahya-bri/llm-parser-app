import json
import os
from typing import Dict, Any, Optional, Union

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from .utils import get_document_as_base64


class DocumentParser:
    """Document parser using Gemini vision model."""
    
    def __init__(
        self, 
        api_key: str = None,
        schema_path: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        model: str = "gemini-2.0-flash",
        temperature: float = 0
    ):
        """Initialize the document parser.
        
        Args:
            api_key: Google API key. If None, tries to use environment variable.
            schema_path: Path to JSON schema file
            schema: Direct schema dict (alternative to schema_path)
            model: Model to use for parsing
            temperature: Temperature for generation
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as GOOGLE_API_KEY environment variable")
            
        # Load schema
        if schema:
            self.json_schema = schema
        elif schema_path:
            with open(schema_path, "r") as schema_file:
                self.json_schema = json.load(schema_file)
        else:
            raise ValueError("Either schema or schema_path must be provided")
            
        self.model = model
        self.temperature = temperature
        
        # Initialize parser model
        self.parsing_model = ChatOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
        ).with_structured_output(self.json_schema)
        
    def parse_document(
        self, 
        document_path: str, 
        page_number: int = 1,
        prompt: str = "You are an AI document extraction specialist. You have been asked to extract structured information from this image"
    ) -> Dict[str, Any]:
        """Parse a document into structured data.
        
        Args:
            document_path: Path to the document (PDF or image)
            page_number: Page number for PDFs (ignored for images)
            prompt: Text prompt to guide the extraction
            
        Returns:
            Structured data based on the schema
        """
        base64_image = get_document_as_base64(document_path, page_number)
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        )
        
        return self.parsing_model.invoke([message])
        
    def parse_base64(
        self, 
        base64_image: str,
        prompt: str = "You are an AI document extraction specialist. You have been asked to extract structured information from this image"
    ) -> Dict[str, Any]:
        """Parse a base64-encoded image into structured data.
        
        Args:
            base64_image: Base64-encoded image string
            prompt: Text prompt to guide the extraction
            
        Returns:
            Structured data based on the schema
        """
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        )
        
        return self.parsing_model.invoke([message])
