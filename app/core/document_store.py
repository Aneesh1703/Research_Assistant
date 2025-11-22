from typing import Dict, List, Optional
from datetime import datetime
import uuid


class DocumentStore:
    # In-memory document store for demonstration purposes
    def __init__(self):
        self._documents: Dict[str, dict] = {}
    

    # Add a new document to the store
    def add_document(self, document_data: dict) -> str:
        document_id = str(uuid.uuid4())
        document_data['document_id'] = document_id
        document_data['created_at'] = datetime.utcnow()
        
        self._documents[document_id] = document_data
        return document_id
    

    # Retrieve a document by its ID
    def get_document(self, document_id: str) -> Optional[dict]:
        return self._documents.get(document_id)
    

    #list documents with optional filters
    def list_documents(
        self, 
        limit: int = 100, 
        offset: int = 0,
        document_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        documents = list(self._documents.values())
        
        if document_type:
            documents = [d for d in documents if d.get('document_type') == document_type]
        if status:
            documents = [d for d in documents if d.get('status') == status]
        
        # Sort by created_at
        documents.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        #pagination
        return documents[offset:offset + limit]
    
    # Delete a document by its ID
    def delete_document(self, document_id: str) -> bool:
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False


    # Update a document by its ID
    def update_document(self, document_id: str, updates: dict) -> bool:
        if document_id in self._documents:
            self._documents[document_id].update(updates)
            return True
        return False
    

    # Simple search implementation
    def search_documents(self, query: str, max_results: int = 5) -> List[dict]:
        query_lower = query.lower()
        results = []
        
        for doc in self._documents.values():
            content = doc.get('content', '').lower()
            title = doc.get('title', '').lower()
            
            # Simple relevance scoring based on keyword matches
            score = 0.0
            
            # Check title match (higher weight)
            if query_lower in title:
                score += 0.5
            
            # Check content match
            if query_lower in content:
                score += 0.3
            
            # Count keyword occurrences
            keyword_count = content.count(query_lower)
            score += min(keyword_count * 0.05, 0.2)
            
            if score > 0:
                results.append({
                    'document': doc,
                    'relevance_score': min(score, 1.0)
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:max_results]
    
    # Get total document count
    def get_total_count(self) -> int:
        return len(self._documents)
    
    # Clear all documents from the store
    def clear(self):
        self._documents.clear()


# Global instance
document_store = DocumentStore()
