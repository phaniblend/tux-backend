from fastapi import APIRouter, HTTPException
from app.models.schemas import RequirementsInput
from app.services.requirements_processor import RequirementsProcessor

router = APIRouter()
requirements_processor = RequirementsProcessor()

@router.post("/process-requirements")
async def process_requirements(requirements: RequirementsInput):
    """Process and validate user requirements"""
    try:
        processed = await requirements_processor.process(requirements)
        return {
            "status": "processed",
            "data": processed,
            "suggestions": await requirements_processor.get_suggestions(requirements)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-requirements")
async def validate_requirements(requirements: RequirementsInput):
    """Validate requirements completeness"""
    try:
        validation_result = await requirements_processor.validate(requirements)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 