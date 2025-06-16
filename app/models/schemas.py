from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class AIModel(str, Enum):
    """Available AI models"""
    LLAMA3_8B = "llama3-8b"
    LLAMA3_70B = "llama3-70b"
    MISTRAL_7B = "mistral-7b"
    MISTRAL_8X7B = "mistral-8x7b"
    QWEN2_72B = "qwen2-72b"
    PHI3_MINI = "phi3-mini"
    OPENCHAT_35 = "openchat-3.5"

class VisionModel(str, Enum):
    """Available vision models"""
    STABLE_DIFFUSION_XL = "stable-diffusion-xl"
    PLAYGROUND_V2 = "playground-v2"
    DALLE3 = "dall-e-3"

# Request Models
class RequirementsInput(BaseModel):
    """Input schema for requirements"""
    purpose: str = Field(..., description="Main purpose of the application")
    audience: str = Field(..., description="Target audience")
    demographics: Optional[str] = Field(None, description="User demographics")
    goals: str = Field(..., description="What users should achieve")
    useCases: List[str] = Field(..., description="Key use cases", alias="use_cases")
    simulateRoles: bool = Field(True, description="Enable multi-role AI analysis", alias="simulate_roles")
    
    class Config:
        populate_by_name = True

class DesignGenerationRequest(BaseModel):
    """Request for generating design specifications"""
    requirements: RequirementsInput
    preferred_llm: Optional[AIModel] = AIModel.LLAMA3_70B

class MockupGenerationRequest(BaseModel):
    """Request for generating UI mockups"""
    ux_specs: Dict[str, Any]
    preferred_vision_model: Optional[VisionModel] = VisionModel.STABLE_DIFFUSION_XL
    image_style: Optional[str] = "clean wireframe"
    image_size: Optional[str] = "1024x1024"

# Response Models
class RoleInsight(BaseModel):
    """Multi-role AI analysis insight"""
    designer: Optional[str] = None
    analyst: Optional[str] = None
    architect: Optional[str] = None

class ScreenElement(BaseModel):
    """Individual screen element"""
    name: str
    description: str
    elements: List[str]
    userFlow: Optional[str] = None
    interactions: Optional[List[str]] = None

class UXSpecification(BaseModel):
    """Generated UX specification"""
    roleInsights: Optional[RoleInsight] = None
    screens: List[ScreenElement]
    ia_structure: Dict[str, Any]
    standards: Dict[str, Any]
    final_prompt_for_image_model: str

class Mockup(BaseModel):
    """Generated mockup"""
    id: str
    screenName: str
    description: str
    imageUrl: str
    generatedAt: str

class MockupResponse(BaseModel):
    """Response containing generated mockups"""
    mockups: List[Mockup]
    total_generated: int
    generation_time: float

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    ai_services: Dict[str, str]

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_code: Optional[str] = None
    timestamp: str 