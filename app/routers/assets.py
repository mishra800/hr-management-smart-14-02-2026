from fastapi import APIRouter, HTTPException, Depends
from app import schemas
from app.database import get_db
from app.dependencies import get_current_user
from app import models
from datetime import datetime
from typing import List

router = APIRouter(
    prefix="/assets",
    tags=["assets"]
)

# Mock assets data
MOCK_ASSETS = {
    1: {
        "id": 1,
        "name": "MacBook Pro 16\"",
        "type": "Laptop",
        "serial_number": "MBP001",
        "status": "assigned",
        "assigned_to": 1,
        "specifications": {
            "processor": "M2 Pro",
            "memory": "16GB",
            "storage": "512GB SSD"
        },
        "location": "Engineering Floor",
        "created_at": datetime.now().isoformat()
    },
    2: {
        "id": 2,
        "name": "Dell Monitor 27\"",
        "type": "Monitor",
        "serial_number": "MON001",
        "status": "available",
        "assigned_to": None,
        "specifications": {
            "size": "27 inch",
            "resolution": "4K",
            "type": "LED"
        },
        "location": "Storage Room",
        "created_at": datetime.now().isoformat()
    },
    3: {
        "id": 3,
        "name": "iPhone 14 Pro",
        "type": "Mobile",
        "serial_number": "IPH001",
        "status": "assigned",
        "assigned_to": 2,
        "specifications": {
            "model": "iPhone 14 Pro",
            "storage": "256GB",
            "color": "Space Black"
        },
        "location": "HR Department",
        "created_at": datetime.now().isoformat()
    }
}

@router.get("/")
def get_assets(current_user: models.User = Depends(get_current_user)):
    """Get all assets"""
    assets = list(MOCK_ASSETS.values())
    
    return schemas.APIResponse(
        success=True,
        message="Assets retrieved successfully",
        data=assets
    )

@router.get("/{asset_id}")
def get_asset(asset_id: int, current_user: models.User = Depends(get_current_user)):
    """Get specific asset"""
    asset = MOCK_ASSETS.get(asset_id)
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return schemas.APIResponse(
        success=True,
        message="Asset retrieved successfully",
        data=asset
    )

@router.post("/")
def create_asset(asset: schemas.AssetCreate, current_user: models.User = Depends(get_current_user)):
    """Create new asset - Admin/Assets team only"""
    if current_user.role not in ["admin", "assets_team"]:
        raise HTTPException(status_code=403, detail="Only admin or assets team can create assets")
    
    db = get_db()
    
    new_id = max(MOCK_ASSETS.keys()) + 1 if MOCK_ASSETS else 1
    new_asset = {
        "id": new_id,
        "name": asset.name,
        "type": asset.type,
        "serial_number": asset.serial_number,
        "status": "available",
        "assigned_to": None,
        "specifications": asset.specifications or {},
        "location": "Storage Room",
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_ASSETS[new_id] = new_asset
    
    return schemas.APIResponse(
        success=True,
        message="Asset created successfully",
        data=new_asset
    )

@router.put("/{asset_id}/assign")
def assign_asset(asset_id: int, assignment: schemas.AssetAssign, current_user: models.User = Depends(get_current_user)):
    """Assign asset to employee - Admin/Assets team only"""
    if current_user.role not in ["admin", "assets_team"]:
        raise HTTPException(status_code=403, detail="Only admin or assets team can assign assets")
    
    if asset_id not in MOCK_ASSETS:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset = MOCK_ASSETS[asset_id]
    
    if asset["status"] == "assigned":
        raise HTTPException(status_code=400, detail="Asset is already assigned")
    
    asset["assigned_to"] = assignment.employee_id
    asset["status"] = "assigned"
    asset["assigned_at"] = datetime.now().isoformat()
    
    return schemas.APIResponse(
        success=True,
        message="Asset assigned successfully",
        data=asset
    )

@router.put("/{asset_id}/unassign")
def unassign_asset(asset_id: int, current_user: models.User = Depends(get_current_user)):
    """Unassign asset from employee - Admin/Assets team only"""
    if current_user.role not in ["admin", "assets_team"]:
        raise HTTPException(status_code=403, detail="Only admin or assets team can unassign assets")
    
    if asset_id not in MOCK_ASSETS:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset = MOCK_ASSETS[asset_id]
    
    if asset["status"] != "assigned":
        raise HTTPException(status_code=400, detail="Asset is not currently assigned")
    
    asset["assigned_to"] = None
    asset["status"] = "available"
    asset["unassigned_at"] = datetime.now().isoformat()
    
    return schemas.APIResponse(
        success=True,
        message="Asset unassigned successfully",
        data=asset
    )

@router.get("/employee/{employee_id}")
def get_employee_assets(employee_id: int, current_user: models.User = Depends(get_current_user)):
    """Get assets assigned to specific employee"""
    employee_assets = [
        asset for asset in MOCK_ASSETS.values()
        if asset.get("assigned_to") == employee_id
    ]
    
    return schemas.APIResponse(
        success=True,
        message="Employee assets retrieved successfully",
        data=employee_assets
    )

@router.get("/types/list")
def get_asset_types(current_user: models.User = Depends(get_current_user)):
    """Get list of asset types"""
    types = [
        {"value": "laptop", "label": "Laptop"},
        {"value": "desktop", "label": "Desktop Computer"},
        {"value": "monitor", "label": "Monitor"},
        {"value": "mobile", "label": "Mobile Phone"},
        {"value": "tablet", "label": "Tablet"},
        {"value": "keyboard", "label": "Keyboard"},
        {"value": "mouse", "label": "Mouse"},
        {"value": "headset", "label": "Headset"},
        {"value": "printer", "label": "Printer"},
        {"value": "other", "label": "Other"}
    ]
    
    return schemas.APIResponse(
        success=True,
        message="Asset types retrieved successfully",
        data=types
    )