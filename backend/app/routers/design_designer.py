from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

router = APIRouter(prefix="/dataset-designer", tags=["Dataset Designer"])

# In-memory store for preview/demo (replace with DB logic in production)
dataset_designer_store = {}

class DatasetDesigner(BaseModel):
    dataset_designer_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    dataset_type: str
    source_type: str = "file"
    file_formats: List[str] = []
    governing_body: Optional[str] = None
    data_standards: List[str] = []
    business_owner: Optional[str] = None
    data_steward: Optional[str] = None
    ingestion_pattern: str = "standard"
    target_schema_type: str = "staging"
    status: str = "draft"
    is_active: bool = True
    tags: List[str] = []

@router.get("/", response_model=List[DatasetDesigner])
def list_dataset_designers():
    return list(dataset_designer_store.values())

@router.get("/{dataset_designer_id}", response_model=DatasetDesigner)
def get_dataset_designer(dataset_designer_id: str):
    dataset_designer = dataset_designer_store.get(dataset_designer_id)
    if not dataset_designer:
        raise HTTPException(status_code=404, detail="Dataset Designer not found")
    return dataset_designer

@router.post("/", response_model=DatasetDesigner)
def create_dataset_designer(dataset_designer: DatasetDesigner):
    if dataset_designer.dataset_designer_id in dataset_designer_store:
        raise HTTPException(status_code=400, detail="Dataset Designer already exists")
    dataset_designer_store[dataset_designer.dataset_designer_id] = dataset_designer
    return dataset_designer

@router.put("/{dataset_designer_id}", response_model=DatasetDesigner)
def update_dataset_designer(dataset_designer_id: str, dataset_designer: DatasetDesigner):
    if dataset_designer_id not in dataset_designer_store:
        raise HTTPException(status_code=404, detail="Dataset Designer not found")
    dataset_designer_store[dataset_designer_id] = dataset_designer
    return dataset_designer

@router.delete("/{dataset_designer_id}")
def delete_dataset_designer(dataset_designer_id: str):
    if dataset_designer_id not in dataset_designer_store:
        raise HTTPException(status_code=404, detail="Dataset Designer not found")
    del dataset_designer_store[dataset_designer_id]
    return {"message": "Dataset Designer deleted"} 