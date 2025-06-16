import logging
from typing import Dict, Any, Optional
from app.models.schemas import RequirementsInput, UXSpecification, RoleInsight, ScreenElement, AIModel
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class UXGenerator:
    """
    UX Generator service that orchestrates the generation of UX specifications
    using multi-role AI analysis and LLM services
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def generate_specifications(
        self, 
        requirements: RequirementsInput,
        preferred_model: AIModel = AIModel.LLAMA3_70B
    ) -> UXSpecification:
        """
        Generate comprehensive UX specifications from requirements
        """
        try:
            logger.info(f"Starting UX specification generation for: {requirements.purpose}")
            
            # Step 1: Multi-role analysis if enabled
            role_insights = None
            if requirements.simulateRoles:
                logger.info("Generating multi-role AI analysis")
                role_insights_dict = await self.llm_service.generate_multi_role_analysis(
                    requirements, preferred_model
                )
                role_insights = RoleInsight(**role_insights_dict)
            
            # Step 2: Generate detailed UX specifications
            logger.info("Generating detailed UX specifications")
            ux_specs_dict = await self.llm_service.generate_ux_specifications(
                requirements, 
                role_insights_dict if role_insights else None
            )
            
            # Step 3: Parse and structure the response
            screens = []
            for screen_data in ux_specs_dict.get("screens", []):
                screen = ScreenElement(
                    name=screen_data.get("name", "Untitled Screen"),
                    description=screen_data.get("description", ""),
                    elements=screen_data.get("elements", []),
                    userFlow=screen_data.get("userFlow"),
                    interactions=screen_data.get("interactions", [])
                )
                screens.append(screen)
            
            # Step 4: Create final UX specification
            ux_specification = UXSpecification(
                roleInsights=role_insights,
                screens=screens,
                ia_structure=ux_specs_dict.get("ia_structure", {}),
                standards=ux_specs_dict.get("standards", {}),
                final_prompt_for_image_model=ux_specs_dict.get(
                    "final_prompt_for_image_model", 
                    self._generate_fallback_prompt(requirements)
                )
            )
            
            logger.info(f"Successfully generated UX specifications with {len(screens)} screens")
            return ux_specification
            
        except Exception as e:
            logger.error(f"Error generating UX specifications: {str(e)}")
            # Return fallback specifications
            return await self._generate_fallback_specifications(requirements)
    
    async def _generate_fallback_specifications(self, requirements: RequirementsInput) -> UXSpecification:
        """Generate basic fallback specifications when LLM fails"""
        logger.warning("Generating fallback UX specifications")
        
        # Create basic screens based on common app patterns
        screens = []
        
        # Dashboard/Home screen
        screens.append(ScreenElement(
            name="Dashboard",
            description=f"Main overview screen for {requirements.purpose}",
            elements=["header", "navigation", "main_content", "quick_actions"],
            userFlow="Users land here to get an overview and access main features",
            interactions=["view_overview", "navigate_to_features", "quick_actions"]
        ))
        
        # Main feature screens based on use cases
        for i, use_case in enumerate(requirements.useCases[:3]):  # Limit to 3 screens
            screen_name = f"Feature {i+1}"
            if "log" in use_case.lower() or "track" in use_case.lower():
                screen_name = "Tracking"
            elif "view" in use_case.lower() or "browse" in use_case.lower():
                screen_name = "Browse"
            elif "manage" in use_case.lower() or "edit" in use_case.lower():
                screen_name = "Management"
            
            screens.append(ScreenElement(
                name=screen_name,
                description=f"Screen for: {use_case}",
                elements=["header", "form_inputs", "action_buttons", "data_display"],
                userFlow=f"Users access this screen to: {use_case}",
                interactions=["input_data", "submit_form", "view_results"]
            ))
        
        return UXSpecification(
            roleInsights=RoleInsight(
                designer="Focus on clean, intuitive interface design with clear visual hierarchy",
                analyst="Ensure all user requirements are met with efficient workflows",
                architect="Structure information logically with scalable navigation patterns"
            ),
            screens=screens,
            ia_structure={
                "navigation": "Top-level navigation with clear categories",
                "hierarchy": "Dashboard → Feature screens → Detail views",
                "relationships": "Linear flow with cross-navigation options"
            },
            standards={
                "accessibility": "WCAG 2.1 AA compliance with proper ARIA labels",
                "responsive": "Mobile-first design with breakpoints at 768px and 1024px",
                "patterns": "Material Design principles with consistent spacing and typography"
            },
            final_prompt_for_image_model=self._generate_fallback_prompt(requirements)
        )
    
    def _generate_fallback_prompt(self, requirements: RequirementsInput) -> str:
        """Generate a basic prompt for image generation"""
        return f"""
Create a clean, modern UI mockup for {requirements.purpose}.
Target audience: {requirements.audience}
Key features: {', '.join(requirements.useCases[:3])}
Style: Clean, professional, mobile-friendly interface with good typography and spacing.
Include: Header navigation, main content area, clear call-to-action buttons.
Color scheme: Modern, accessible colors with good contrast ratios.
""" 