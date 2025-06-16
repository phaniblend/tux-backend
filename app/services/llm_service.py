import os
import httpx
import json
import logging
from typing import Dict, Any, Optional
from app.models.schemas import AIModel, RequirementsInput

logger = logging.getLogger(__name__)

class LLMService:
    """
    LLM Service for integrating with open-source AI models
    Following TUX.txt specification for HuggingFace, Together.ai, etc.
    """
    
    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_API_KEY")
        self.together_token = os.getenv("TOGETHER_API_KEY")
        self.base_urls = {
            "huggingface": "https://api-inference.huggingface.co/models/",
            "together": "https://api.together.xyz/inference"
        }
        
    async def generate_multi_role_analysis(
        self, 
        requirements: RequirementsInput, 
        model: AIModel = AIModel.LLAMA3_70B
    ) -> Dict[str, Any]:
        """
        Generate multi-role UX analysis using AI
        Simulates Product Designer, Business Analyst, and UX Architect
        """
        
        prompt = self._build_multi_role_prompt(requirements)
        
        try:
            if model in [AIModel.LLAMA3_70B, AIModel.LLAMA3_8B]:
                response = await self._call_together_api(prompt, model)
            else:
                response = await self._call_huggingface_api(prompt, model)
                
            return self._parse_multi_role_response(response)
            
        except Exception as e:
            logger.error(f"Error in multi-role analysis: {str(e)}")
            # Fallback to simpler model
            return await self._fallback_analysis(requirements)
    
    async def generate_ux_specifications(
        self, 
        requirements: RequirementsInput,
        role_insights: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate detailed UX specifications"""
        
        prompt = self._build_ux_spec_prompt(requirements, role_insights)
        
        try:
            response = await self._call_llm(prompt, AIModel.LLAMA3_70B)
            return self._parse_ux_spec_response(response)
        except Exception as e:
            logger.error(f"Error generating UX specs: {str(e)}")
            raise
    
    def _build_multi_role_prompt(self, requirements: RequirementsInput) -> str:
        """Build prompt for multi-role analysis as specified in TUX.txt"""
        return f"""
You are an expert UX design team consisting of three roles:
1. Product Designer - Focuses on user experience, interface design, and usability
2. Business Analyst - Focuses on requirements analysis, user stories, and business logic  
3. UX Architect - Focuses on information architecture, user flows, and system design

Analyze the following application requirements from each perspective:

Purpose: {requirements.purpose}
Target Audience: {requirements.audience}
Demographics: {requirements.demographics or 'Not specified'}
User Goals: {requirements.goals}
Use Cases: {', '.join(requirements.useCases)}

For each role, provide insights in JSON format:
{{
    "designer": "Product Designer insights and recommendations",
    "analyst": "Business Analyst insights and requirements breakdown", 
    "architect": "UX Architect insights on information architecture and flows"
}}

Focus on:
- User experience best practices
- Accessibility standards
- Modern design patterns
- Technical feasibility
- Business value
"""

    def _build_ux_spec_prompt(self, requirements: RequirementsInput, role_insights: Optional[Dict[str, str]]) -> str:
        """Build prompt for detailed UX specifications"""
        insights_text = ""
        if role_insights:
            insights_text = f"""
Previous Role Analysis:
- Designer: {role_insights.get('designer', '')}
- Analyst: {role_insights.get('analyst', '')}
- Architect: {role_insights.get('architect', '')}
"""
        
        return f"""
Based on the following requirements, generate comprehensive UX specifications:

{insights_text}

Requirements:
Purpose: {requirements.purpose}
Audience: {requirements.audience}
Demographics: {requirements.demographics or 'Not specified'}
Goals: {requirements.goals}
Use Cases: {', '.join(requirements.useCases)}

Generate a detailed UX specification in JSON format with:
{{
    "screens": [
        {{
            "name": "Screen Name",
            "description": "What this screen does",
            "elements": ["list", "of", "ui", "elements"],
            "userFlow": "How users interact with this screen",
            "interactions": ["list", "of", "interactions"]
        }}
    ],
    "ia_structure": {{
        "navigation": "Main navigation structure",
        "hierarchy": "Information hierarchy",
        "relationships": "How screens connect"
    }},
    "standards": {{
        "accessibility": "Accessibility requirements",
        "responsive": "Responsive design approach",
        "patterns": "UI patterns to use"
    }},
    "final_prompt_for_image_model": "Detailed prompt for generating UI mockups"
}}

Focus on modern UX best practices, accessibility, and user-centered design.
"""

    async def _call_together_api(self, prompt: str, model: AIModel) -> str:
        """Call Together.AI API for Llama models"""
        if not self.together_token:
            raise Exception("Together.AI API token not configured")
            
        model_map = {
            AIModel.LLAMA3_70B: "meta-llama/Llama-3-70b-chat-hf",
            AIModel.LLAMA3_8B: "meta-llama/Llama-3-8b-chat-hf"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.together.xyz/inference",
                headers={
                    "Authorization": f"Bearer {self.together_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_map.get(model, model_map[AIModel.LLAMA3_8B]),
                    "prompt": prompt,
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Together.AI API error: {response.text}")
                
            return response.json()["output"]["choices"][0]["text"]
    
    async def _call_huggingface_api(self, prompt: str, model: AIModel) -> str:
        """Call HuggingFace Inference API"""
        if not self.hf_token:
            raise Exception("HuggingFace API token not configured")
            
        model_map = {
            AIModel.MISTRAL_7B: "mistralai/Mistral-7B-Instruct-v0.1",
            AIModel.MISTRAL_8X7B: "mistralai/Mixtral-8x7B-Instruct-v0.1",
            AIModel.PHI3_MINI: "microsoft/Phi-3-mini-4k-instruct",
            AIModel.QWEN2_72B: "Qwen/Qwen2-72B-Instruct"
        }
        
        model_name = model_map.get(model, model_map[AIModel.MISTRAL_7B])
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_urls['huggingface']}{model_name}",
                headers={
                    "Authorization": f"Bearer {self.hf_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 2048,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "return_full_text": False
                    }
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"HuggingFace API error: {response.text}")
                
            result = response.json()
            if isinstance(result, list):
                return result[0]["generated_text"]
            return result["generated_text"]
    
    async def _call_llm(self, prompt: str, model: AIModel) -> str:
        """Generic LLM call router"""
        if model in [AIModel.LLAMA3_70B, AIModel.LLAMA3_8B]:
            return await self._call_together_api(prompt, model)
        else:
            return await self._call_huggingface_api(prompt, model)
    
    def _parse_multi_role_response(self, response: str) -> Dict[str, str]:
        """Parse multi-role analysis response"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._extract_role_insights(response)
        except Exception as e:
            logger.error(f"Error parsing multi-role response: {str(e)}")
            return {"designer": "", "analyst": "", "architect": ""}
    
    def _parse_ux_spec_response(self, response: str) -> Dict[str, Any]:
        """Parse UX specification response"""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise Exception("Could not extract JSON from response")
        except Exception as e:
            logger.error(f"Error parsing UX spec response: {str(e)}")
            raise Exception(f"Failed to parse AI response: {str(e)}")
    
    def _extract_role_insights(self, response: str) -> Dict[str, str]:
        """Fallback method to extract role insights from unstructured text"""
        insights = {"designer": "", "analyst": "", "architect": ""}
        
        # Simple pattern matching
        lines = response.split('\n')
        current_role = None
        
        for line in lines:
            line = line.strip()
            if 'designer' in line.lower():
                current_role = 'designer'
            elif 'analyst' in line.lower():
                current_role = 'analyst'  
            elif 'architect' in line.lower():
                current_role = 'architect'
            elif current_role and line:
                insights[current_role] += line + " "
        
        return insights
    
    async def _fallback_analysis(self, requirements: RequirementsInput) -> Dict[str, str]:
        """Fallback multi-role analysis using simpler approach"""
        return {
            "designer": f"Design a user-friendly interface for {requirements.purpose} targeting {requirements.audience}. Focus on accessibility and modern UI patterns.",
            "analyst": f"Break down the requirements: Purpose is {requirements.purpose}. Key use cases: {', '.join(requirements.useCases)}. Ensure business value alignment.",
            "architect": f"Structure the information architecture around {requirements.goals}. Plan user flows for {len(requirements.useCases)} main use cases."
        }

    async def generate_html_layout(self, prompt: str) -> str:
        """
        Generate HTML/CSS layout from UX specifications.
        Replaces image generation with clean, editable HTML layouts.
        """
        try:
            # Try with the primary model first (Llama-3-70B)
            response = await self._call_llm(prompt, AIModel.LLAMA3_70B)
            
            if response and "<div" in response.lower():
                return response
            
            # Fallback to other models
            models_to_try = [AIModel.LLAMA3_8B, AIModel.MISTRAL_7B, AIModel.PHI3_MINI]
            
            for model in models_to_try:
                try:
                    response = await self._call_llm(prompt, model)
                    if response and "<div" in response.lower():
                        return response
                        
                except Exception as e:
                    logger.warning(f"Model {model} failed for HTML generation: {str(e)}")
                    continue
            
            # If all models fail, return a basic HTML structure
            return self._generate_basic_html_fallback()
            
        except Exception as e:
            logger.error(f"HTML generation failed: {str(e)}")
            return self._generate_basic_html_fallback()
    
    def _generate_basic_html_fallback(self) -> str:
        """
        Generate a basic HTML fallback when all LLM calls fail.
        """
        return """
        <div style="width: 100%; min-height: 100vh; background: #f8fafc; font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;">
            <header style="background: #3b82f6; color: white; padding: 1.5rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="margin: 0; font-size: 1.75rem; font-weight: 600;">Application Screen</h1>
            </header>
            
            <main style="padding: 2rem; max-width: 1200px; margin: 0 auto;">
                <div style="background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e5e7eb;">
                    <h2 style="margin: 0 0 1.5rem 0; color: #1f2937; font-size: 1.5rem; font-weight: 600;">Welcome</h2>
                    <p style="color: #6b7280; line-height: 1.6; margin-bottom: 2rem;">This is a placeholder screen layout. The actual content will be generated based on your requirements.</p>
                    
                    <div style="display: grid; gap: 1rem; margin-bottom: 2rem;">
                        <button style="background: #10b981; color: white; border: none; border-radius: 8px; padding: 0.875rem 2rem; font-weight: 500; font-size: 1rem; cursor: pointer; transition: all 0.2s; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);">
                            Primary Action
                        </button>
                        <button style="background: #f3f4f6; color: #374151; border: 1px solid #d1d5db; border-radius: 8px; padding: 0.875rem 2rem; font-weight: 500; font-size: 1rem; cursor: pointer; transition: all 0.2s;">
                            Secondary Action
                        </button>
                    </div>
                    
                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem;">
                        <h3 style="margin: 0 0 0.5rem 0; color: #111827; font-size: 1.125rem; font-weight: 500;">Information Panel</h3>
                        <p style="margin: 0; color: #6b7280; font-size: 0.875rem;">Additional content and information would appear here based on your specific requirements.</p>
                    </div>
                </div>
            </main>
        </div>
        """ 