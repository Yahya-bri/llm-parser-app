import os
import json
import sys
from pprint import pprint

# Add parent directory to path to import package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vision_parser import ParserService

# Example usage
def main():
    # You can set this in environment variables
    api_key = os.environ.get("GOOGLE_API_KEY", "your_api_key_here")
    
    # Path to schemas folder
    schemas_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "schemas"))
    
    # Initialize the parser service
    parser_service = ParserService(
        api_key=api_key,
        schema_dir=schemas_dir,
        default_schema="resume"
    )
    
    # Path to the resume PDF
    resume_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "Yahya_BRITAL_CV (26).pdf"))
    
    # Parse the resume
    result = parser_service.parse_document(
        document_path=resume_path,
        page_number=1
    )
    
    # Print the results
    print("Parsed Resume:")
    pprint(result)
    
    # Save the results to a JSON file
    output_path = os.path.join(os.path.dirname(__file__), "parsed_resume.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
