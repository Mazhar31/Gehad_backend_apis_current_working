from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.portfolio_case import PortfolioCaseCreate, PortfolioCaseUpdate, PortfolioCaseResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin, PortfolioCase
import uuid

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def create_portfolio_case(
    case_data: PortfolioCaseCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new portfolio case"""
    case = PortfolioCase(
        id=f"pc-{uuid.uuid4().hex[:8]}",
        category=case_data.category,
        title=case_data.title,
        description=case_data.description,
        link=case_data.link,
        is_public=case_data.is_public
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    return ResponseModel(
        data=PortfolioCaseResponse.from_orm(case).dict(),
        message="Portfolio case created successfully"
    )


@router.get("/", response_model=ResponseModel)
async def get_portfolio_cases(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get list of portfolio cases"""
    cases = db.query(PortfolioCase).all()
    return ResponseModel(
        data=[PortfolioCaseResponse.from_orm(case).dict() for case in cases],
        message="Portfolio cases retrieved successfully"
    )


@router.put("/{case_id}", response_model=ResponseModel)
async def update_portfolio_case(
    case_id: str,
    case_data: PortfolioCaseUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update portfolio case"""
    case = db.query(PortfolioCase).filter(PortfolioCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Portfolio case not found")
    
    update_data = case_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)
    
    db.commit()
    db.refresh(case)
    
    return ResponseModel(
        data=PortfolioCaseResponse.from_orm(case).dict(),
        message="Portfolio case updated successfully"
    )


@router.delete("/{case_id}", response_model=ResponseModel)
async def delete_portfolio_case(
    case_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete portfolio case"""
    case = db.query(PortfolioCase).filter(PortfolioCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Portfolio case not found")
    
    db.delete(case)
    db.commit()
    
    return ResponseModel(message="Portfolio case deleted successfully")


# Public endpoint for portfolio cases
@router.get("/public", response_model=ResponseModel)
async def get_public_portfolio_cases(db: Session = Depends(get_db)):
    """Get public portfolio cases (no authentication required)"""
    cases = db.query(PortfolioCase).filter(PortfolioCase.is_public == True).all()
    return ResponseModel(
        data=[PortfolioCaseResponse.from_orm(case).dict() for case in cases],
        message="Public portfolio cases retrieved successfully"
    )