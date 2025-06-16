import logging
from typing import Dict, Any, List
from app.models.schemas import RequirementsInput

logger = logging.getLogger(__name__)

class RequirementsProcessor:
    """
    Service for processing and validating user requirements
    """
    
    def __init__(self):
        self.required_fields = ['purpose', 'audience', 'goals', 'use_cases']
        self.optional_fields = ['demographics', 'simulate_roles']
    
    async def process(self, requirements: RequirementsInput) -> Dict[str, Any]:
        """Process and enrich requirements"""
        try:
            logger.info(f"Processing requirements for: {requirements.purpose}")
            
            # Basic processing
            processed = {
                "purpose": requirements.purpose.strip(),
                "audience": requirements.audience.strip(),
                "demographics": requirements.demographics.strip() if requirements.demographics else None,
                "goals": requirements.goals.strip(),
                "use_cases": [uc.strip() for uc in requirements.useCases if uc.strip()],
                "simulate_roles": requirements.simulateRoles,
                "processed_at": "2024-01-01T00:00:00Z",  # Would use actual timestamp
                "completeness_score": self._calculate_completeness(requirements)
            }
            
            # Add derived insights
            processed["insights"] = await self._generate_insights(requirements)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing requirements: {str(e)}")
            raise
    
    async def validate(self, requirements: RequirementsInput) -> Dict[str, Any]:
        """Validate requirements completeness and quality"""
        try:
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "suggestions": [],
                "completeness_score": 0
            }
            
            # Check required fields
            if not requirements.purpose or len(requirements.purpose.strip()) < 10:
                validation_result["errors"].append("Purpose must be at least 10 characters long")
                validation_result["is_valid"] = False
            
            if not requirements.audience or len(requirements.audience.strip()) < 5:
                validation_result["errors"].append("Target audience must be specified")
                validation_result["is_valid"] = False
            
            if not requirements.goals or len(requirements.goals.strip()) < 10:
                validation_result["errors"].append("User goals must be clearly defined")
                validation_result["is_valid"] = False
            
            if not requirements.useCases or len(requirements.useCases) < 1:
                validation_result["errors"].append("At least one use case must be provided")
                validation_result["is_valid"] = False
            
            # Check for quality warnings
            if len(requirements.useCases) < 3:
                validation_result["warnings"].append("Consider adding more use cases for better UX analysis")
            
            if not requirements.demographics:
                validation_result["warnings"].append("Demographics information would help create more targeted designs")
            
            # Calculate completeness score
            validation_result["completeness_score"] = self._calculate_completeness(requirements)
            
            # Add suggestions
            validation_result["suggestions"] = await self.get_suggestions(requirements)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating requirements: {str(e)}")
            raise
    
    async def get_suggestions(self, requirements: RequirementsInput) -> List[str]:
        """Get suggestions for improving requirements"""
        suggestions = []
        
        try:
            # Purpose-based suggestions
            if "app" in requirements.purpose.lower():
                if "mobile" not in requirements.purpose.lower() and "web" not in requirements.purpose.lower():
                    suggestions.append("Consider specifying if this is a mobile app, web app, or both")
            
            # Audience-based suggestions
            if "users" in requirements.audience.lower() and not requirements.demographics:
                suggestions.append("Adding demographic details (age, tech-savviness, etc.) would improve the design")
            
            # Use case suggestions
            if len(requirements.useCases) < 3:
                suggestions.append("Adding more specific use cases will result in more comprehensive UX specifications")
            
            # Goal-based suggestions
            if "manage" in requirements.goals.lower() or "track" in requirements.goals.lower():
                suggestions.append("Consider adding use cases for data visualization and reporting")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return []
    
    def _calculate_completeness(self, requirements: RequirementsInput) -> float:
        """Calculate completeness score (0-100)"""
        score = 0
        
        # Required fields (60 points total)
        if requirements.purpose and len(requirements.purpose.strip()) >= 10:
            score += 15
        if requirements.audience and len(requirements.audience.strip()) >= 5:
            score += 15
        if requirements.goals and len(requirements.goals.strip()) >= 10:
            score += 15
        if requirements.useCases and len(requirements.useCases) >= 1:
            score += 15
        
        # Quality factors (40 points total)
        if requirements.demographics:
            score += 10
        if len(requirements.useCases) >= 3:
            score += 10
        if len(requirements.purpose) >= 50:  # Detailed purpose
            score += 10
        if len(requirements.goals) >= 50:  # Detailed goals
            score += 10
        
        return min(score, 100)
    
    async def _generate_insights(self, requirements: RequirementsInput) -> Dict[str, str]:
        """Generate basic insights about the requirements"""
        insights = {}
        
        try:
            # App type insight
            purpose_lower = requirements.purpose.lower()
            if any(word in purpose_lower for word in ['fitness', 'health', 'workout', 'exercise']):
                insights["app_category"] = "Health & Fitness"
            elif any(word in purpose_lower for word in ['business', 'productivity', 'work', 'task']):
                insights["app_category"] = "Business & Productivity"
            elif any(word in purpose_lower for word in ['social', 'chat', 'message', 'community']):
                insights["app_category"] = "Social & Communication"
            else:
                insights["app_category"] = "General Application"
            
            # Complexity insight
            if len(requirements.useCases) >= 5:
                insights["complexity"] = "High - Multiple features and workflows"
            elif len(requirements.useCases) >= 3:
                insights["complexity"] = "Medium - Several key features"
            else:
                insights["complexity"] = "Low - Simple, focused functionality"
            
            # Target platform suggestion
            audience_lower = requirements.audience.lower()
            if any(word in audience_lower for word in ['mobile', 'phone', 'on-the-go']):
                insights["recommended_platform"] = "Mobile-first design recommended"
            elif any(word in audience_lower for word in ['professional', 'business', 'office']):
                insights["recommended_platform"] = "Desktop/web application recommended"
            else:
                insights["recommended_platform"] = "Cross-platform approach recommended"
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {} 