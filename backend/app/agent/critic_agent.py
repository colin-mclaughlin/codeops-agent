import os
import openai
import re
from backend.app.utils.logging import get_logger
from backend.app.config import settings
from datetime import datetime
from typing import Dict, Any

logger = get_logger(__name__)


class CriticAgent:
    """
    Secondary reasoning agent that critiques the main LangGraph plan and reflection.
    Provides quality assessment, risk identification, and confidence scoring.
    """

    def __init__(self):
        """
        Initialize CriticAgent with OpenAI configuration.
        """
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured in .env")
        
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("CriticAgent initialized successfully")

    async def critique(self, plan: str, reflection: str, context: str = "") -> Dict[str, Any]:
        """
        Review the main agent's plan and reflection for quality, risks, and confidence.
        
        Args:
            plan: The primary agent's action plan
            reflection: The primary agent's reflection on the plan
            context: Optional additional context for the critique
            
        Returns:
            Dictionary with critique text, confidence score, and metadata
        """
        try:
            system_prompt = (
                "You are a critical reviewer of another AI agent's reasoning and planning. "
                "Your role is to:\n"
                "1. Evaluate the quality and completeness of the proposed plan\n"
                "2. Identify potential risks, gaps, or missing considerations\n"
                "3. Assess the reflection's depth and self-awareness\n"
                "4. Provide a confidence score (0-100) based on overall quality\n"
                "5. Suggest specific improvements if needed\n\n"
                "Be analytical, constructive, and concise. Focus on actionable feedback."
            )

            context_section = f"=== ADDITIONAL CONTEXT ===\n{context}\n\n" if context else ""
            
            user_prompt = f"""Review the following primary agent output:

=== PRIMARY AGENT PLAN ===
{plan}

=== PRIMARY AGENT REFLECTION ===
{reflection}

{context_section}Please provide:
1. **Key Strengths**: What the agent did well
2. **Weaknesses & Risks**: Potential issues or missing elements
3. **Confidence Assessment**: Score 0-100 with brief justification
4. **Improvement Suggestions**: Specific recommendations

Format your response clearly with headers for each section."""

            completion = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for consistent critique
                max_tokens=800
            )
            
            critique_text = completion.choices[0].message.content.strip()
            
            # Extract confidence score from the critique text
            confidence = self._extract_confidence_score(critique_text)
            
            logger.info(f"CriticAgent critique completed with confidence: {confidence}")
            
            return {
                "critique": critique_text,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat(),
                "plan_length": len(plan),
                "reflection_length": len(reflection)
            }
            
        except Exception as e:
            logger.error(f"CriticAgent critique failed: {e}")
            return {
                "critique": f"Error: Unable to generate critique - {str(e)}",
                "confidence": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    def _extract_confidence_score(self, critique_text: str) -> int:
        """
        Extract confidence score from critique text using pattern matching.
        
        Args:
            critique_text: The full critique text
            
        Returns:
            Confidence score as integer (0-100)
        """
        try:
            # Look for confidence score patterns
            patterns = [
                r'confidence[:\s]+(\d+)',
                r'score[:\s]+(\d+)',
                r'(\d+)[\s]*%',
                r'(\d+)/100',
                r'rating[:\s]+(\d+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, critique_text.lower())
                if matches:
                    score = int(matches[0])
                    if 0 <= score <= 100:
                        return score
            
            # Look for any number between 0-100 in the text
            numbers = re.findall(r'\b(\d+)\b', critique_text)
            for num in numbers:
                score = int(num)
                if 0 <= score <= 100:
                    return score
            
            # Default to medium confidence if no score found
            logger.warning("No confidence score found in critique, defaulting to 70")
            return 70
            
        except Exception as e:
            logger.warning(f"Error extracting confidence score: {e}, defaulting to 70")
            return 70

    async def quick_review(self, plan: str) -> Dict[str, Any]:
        """
        Perform a quick review of just the plan (without reflection).
        
        Args:
            plan: The action plan to review
            
        Returns:
            Dictionary with quick critique results
        """
        try:
            system_prompt = (
                "You are a quick reviewer of action plans. "
                "Provide a brief assessment focusing on feasibility and completeness. "
                "Give a confidence score (0-100) and highlight any major concerns."
            )

            user_prompt = f"""Quick review of this action plan:

{plan}

Provide:
1. Feasibility assessment
2. Major concerns or gaps
3. Confidence score (0-100)
4. One key improvement suggestion"""

            completion = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            critique_text = completion.choices[0].message.content.strip()
            confidence = self._extract_confidence_score(critique_text)
            
            logger.info(f"CriticAgent quick review completed with confidence: {confidence}")
            
            return {
                "critique": critique_text,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "quick_review"
            }
            
        except Exception as e:
            logger.error(f"CriticAgent quick review failed: {e}")
            return {
                "critique": f"Error: Unable to perform quick review - {str(e)}",
                "confidence": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    def get_critique_summary(self, critique_result: Dict[str, Any]) -> str:
        """
        Generate a concise summary of the critique for Slack notifications.
        
        Args:
            critique_result: The full critique result dictionary
            
        Returns:
            Formatted summary string for Slack
        """
        confidence = critique_result.get("confidence", 0)
        critique = critique_result.get("critique", "")
        
        # Extract key points from critique
        lines = critique.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line and ('strength' in line.lower() or 'weakness' in line.lower() or 
                        'risk' in line.lower() or 'improvement' in line.lower()):
                key_points.append(f"• {line}")
                if len(key_points) >= 3:  # Limit to 3 key points
                    break
        
        summary = f"🧠 **Critic Review** (Confidence: {confidence}/100)\n\n"
        
        if key_points:
            summary += "\n".join(key_points[:3])
        else:
            # Fallback to first few lines of critique
            summary += critique[:200] + "..." if len(critique) > 200 else critique
        
        return summary
