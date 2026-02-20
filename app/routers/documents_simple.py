from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from datetime import datetime
from typing import List, Optional
import random
import os
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

# Mock document types
DOCUMENT_TYPES = [
    "Identity Documents",
    "Educational Certificates", 
    "Employment Documents",
    "Banking Documents",
    "Personal Documents",
    "Contracts",
    "Policies",
    "Tax Forms",
    "Benefits",
    "Training Materials",
    "General"
]

# Mock documents data
mock_documents = [
    {
        "id": 1,
        "document_type": "Identity Documents",
        "document_url": "uploads/documents/employee_1_20240128_Identity_Documents.pdf",
        "is_verified": True,
        "ocr_confidence": 95.5,
        "uploaded_at": "2024-01-15T10:30:00",
        "rejection_reason": None,
        "verified_by": 1,
        "verified_at": "2024-01-15T11:00:00"
    },
    {
        "id": 2,
        "document_type": "Educational Certificates",
        "document_url": "uploads/documents/employee_1_20240120_Educational_Certificates.pdf",
        "is_verified": False,
        "ocr_confidence": 68.2,
        "uploaded_at": "2024-01-20T14:15:00",
        "rejection_reason": "Low OCR confidence. Please ensure the document is clear and well-lit.",
        "verified_by": None,
        "verified_at": None
    },
    {
        "id": 3,
        "document_type": "Employment Documents",
        "document_url": "uploads/documents/employee_1_20240125_Employment_Documents.pdf",
        "is_verified": True,
        "ocr_confidence": 89.7,
        "uploaded_at": "2024-01-25T09:45:00",
        "rejection_reason": None,
        "verified_by": 1,
        "verified_at": "2024-01-25T10:30:00"
    }
]

@router.get("/types")
def get_document_types():
    """Get available document types"""
    return {"document_types": DOCUMENT_TYPES}

@router.get("/")
def get_my_documents(
    document_type: Optional[str] = None,
    verified_only: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get current user's documents with optional filters"""
    documents = mock_documents.copy()
    
    if document_type:
        documents = [doc for doc in documents if doc["document_type"] == document_type]
    
    if verified_only is not None:
        documents = [doc for doc in documents if doc["is_verified"] == verified_only]
    
    return documents

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    document_type: str = "General",
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Upload a new document"""
    # Validate document type
    if document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid document type. Must be one of: {DOCUMENT_TYPES}")

    # Validate file size (10MB limit)
    if hasattr(file, 'size') and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    # Validate file type
    allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG")
    
    # Mock AI OCR Verification
    ocr_confidence = round(random.uniform(60.0, 99.9), 1)
    is_verified = ocr_confidence >= 75.0
    rejection_reason = None
    
    if not is_verified:
        rejection_reason = "Low OCR confidence. Please ensure the document is clear and well-lit."
    
    # Create mock document record
    new_document = {
        "id": len(mock_documents) + 1,
        "document_type": document_type,
        "document_url": f"uploads/documents/employee_{current_user.get('id', 1)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{document_type.replace(' ', '_')}{file_extension}",
        "is_verified": is_verified,
        "ocr_confidence": ocr_confidence,
        "uploaded_at": datetime.now().isoformat(),
        "rejection_reason": rejection_reason,
        "verified_by": 1 if is_verified else None,
        "verified_at": datetime.now().isoformat() if is_verified else None
    }
    
    mock_documents.append(new_document)
    
    return new_document

@router.get("/{document_id}")
def get_document_details(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get specific document details"""
    document = next((doc for doc in mock_documents if doc["id"] == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Download a document file"""
    document = next((doc for doc in mock_documents if doc["id"] == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # For demo purposes, return a success message
    # In real implementation, this would return FileResponse
    return {
        "message": "Document download initiated",
        "filename": os.path.basename(document["document_url"]),
        "note": "This is a demo - actual file download would happen here"
    }

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a document"""
    global mock_documents
    document = next((doc for doc in mock_documents if doc["id"] == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    mock_documents = [doc for doc in mock_documents if doc["id"] != document_id]
    
    return {"message": "Document deleted successfully"}

@router.get("/statistics")
def get_document_statistics(current_user: dict = Depends(get_current_user)):
    """Get document statistics"""
    total_documents = len(mock_documents)
    verified_documents = len([doc for doc in mock_documents if doc["is_verified"]])
    pending_documents = total_documents - verified_documents
    
    # Documents by type
    type_stats = {}
    for doc_type in DOCUMENT_TYPES:
        count = len([doc for doc in mock_documents if doc["document_type"] == doc_type])
        if count > 0:
            type_stats[doc_type] = count
    
    return {
        "total_documents": total_documents,
        "verified_documents": verified_documents,
        "pending_documents": pending_documents,
        "verification_rate": round((verified_documents / total_documents * 100), 2) if total_documents > 0 else 0,
        "documents_by_type": type_stats
    }