from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType
)
from config import Config
import uuid

class SearchManager:
    def __init__(self):
        self.endpoint = Config.AZURE_SEARCH_ENDPOINT
        self.key = Config.AZURE_SEARCH_API_KEY
        self.index_name = Config.AZURE_SEARCH_INDEX_NAME
        
        self.credential = AzureKeyCredential(self.key)
        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=self.credential
        )
        
        # Create index if it doesn't exist
        self._create_index_if_not_exists()
        
        # Initialize search client
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )
    
    def _create_index_if_not_exists(self):
        """Create the search index if it doesn't exist"""
        try:
            # Check if index exists
            self.index_client.get_index(self.index_name)
            print(f"Index '{self.index_name}' already exists")
        except Exception:
            # Index doesn't exist, create it
            print(f"Creating index '{self.index_name}'...")
            
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="filename", type=SearchFieldDataType.String),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SimpleField(name="owner", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="folder", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="container", type=SearchFieldDataType.String),
                SimpleField(name="filepath", type=SearchFieldDataType.String),
            ]
            
            index = SearchIndex(name=self.index_name, fields=fields)
            self.index_client.create_index(index)
            print(f"Index '{self.index_name}' created successfully")
    
    def index_document(self, filename, content, owner, folder, container, filepath):
        """Index a single document"""
        try:
            doc_id = str(uuid.uuid4())
            
            document = {
                "id": doc_id,
                "filename": filename,
                "content": content,
                "owner": owner,
                "folder": folder,
                "container": container,
                "filepath": filepath
            }
            
            result = self.search_client.upload_documents(documents=[document])
            return True, f"Document indexed with ID: {doc_id}"
        except Exception as e:
            return False, f"Error indexing document: {str(e)}"
    
    def search_documents(self, query, top=10):
        """Search for documents"""
        try:
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            documents = []
            for result in results:
                documents.append({
                    'filename': result['filename'],
                    'owner': result['owner'],
                    'folder': result['folder'],
                    'container': result['container'],
                    'filepath': result['filepath'],
                    'score': result['@search.score']
                })
            
            return documents
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def delete_document(self, doc_id):
        """Delete a document from the index"""
        try:
            self.search_client.delete_documents(documents=[{"id": doc_id}])
            return True, "Document deleted from index"
        except Exception as e:
            return False, f"Error deleting document: {str(e)}"
