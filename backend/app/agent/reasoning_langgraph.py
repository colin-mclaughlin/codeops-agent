import asyncio
from datetime import datetime
from typing import Dict, Any, List
from backend.app.agent.github_tool import GitHubTool
from backend.app.agent.slack_tool import SlackTool
from backend.app.agent.critic_agent import CriticAgent
from backend.app.retrieval import get_context
from backend.app.utils.logging import get_logger
from backend.app.config import settings
import openai
import json

logger = get_logger(__name__)


class LangGraphOrchestrator:
    """
    LangGraph-style reasoning pipeline for CodeOps Agent.
    Supports multi-step planning and reflection with tool integration.
    """

    def __init__(self, repo_name: str = "octocat/Hello-World"):
        """
        Initialize LangGraph orchestrator with tools and configuration.
        
        Args:
            repo_name: GitHub repository name for context and operations
        """
        self.repo_name = repo_name
        self.github = GitHubTool(repo_name)
        self.slack = SlackTool()
        
        # Initialize OpenAI client
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured in .env")
        
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info(f"LangGraphOrchestrator initialized for repository: {repo_name}")

    async def think(self, prompt: str, context: str = "", max_retries: int = 3) -> str:
        """
        Query OpenAI for reasoning output with retry logic.
        
        Args:
            prompt: The reasoning prompt/question
            context: Additional context information
            max_retries: Maximum number of retry attempts
            
        Returns:
            AI-generated reasoning output
        """
        system_prompt = (
            "You are the CodeOps Agent, an expert in CI/CD pipeline diagnosis and automation. "
            "Your role is to:\n"
            "1. Analyze CI/CD failures and build issues\n"
            "2. Propose concrete, actionable fixes\n"
            "3. Consider multiple approaches and trade-offs\n"
            "4. Provide clear reasoning for your decisions\n\n"
            "Always be specific, practical, and focus on solutions that can be automated."
        )
        
        for attempt in range(max_retries):
            try:
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Prompt: {prompt}\n\nContext:\n{context}"}
                    ],
                    temperature=0.1,  # Low temperature for consistent reasoning
                    max_tokens=1000
                )
                
                result = completion.choices[0].message.content.strip()
                logger.info(f"OpenAI reasoning completed (attempt {attempt + 1})")
                return result
                
            except Exception as e:
                logger.warning(f"OpenAI request failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    logger.error("All OpenAI retry attempts failed")
                    return f"Error: Unable to generate reasoning after {max_retries} attempts: {e}"
                await asyncio.sleep(1)  # Brief delay before retry

    async def analyze_context(self, context_snippets: List[str]) -> Dict[str, Any]:
        """
        Analyze retrieved context to identify key issues and patterns.
        
        Args:
            context_snippets: List of context snippets from FAISS retrieval
            
        Returns:
            Dictionary with analysis results
        """
        context_text = "\n".join([f"Snippet {i+1}: {snippet}" for i, snippet in enumerate(context_snippets)])
        
        analysis_prompt = (
            "Analyze the following CI/CD context snippets and identify:\n"
            "1. Primary failure points or issues\n"
            "2. Error patterns or common causes\n"
            "3. Dependencies or configuration problems\n"
            "4. Potential root causes\n\n"
            "Provide a structured analysis with specific findings."
        )
        
        analysis = await self.think(analysis_prompt, context_text)
        
        return {
            "snippet_count": len(context_snippets),
            "analysis": analysis,
            "context_preview": context_text[:500] + "..." if len(context_text) > 500 else context_text
        }

    async def plan_actions(self, analysis: str, context: str) -> Dict[str, Any]:
        """
        Create an actionable plan based on analysis.
        
        Args:
            analysis: Previous analysis results
            context: Original context information
            
        Returns:
            Dictionary with planned actions
        """
        planning_prompt = (
            "Based on the analysis, create a specific action plan to fix the issues:\n"
            "1. List concrete steps to take\n"
            "2. Identify which tools/operations are needed\n"
            "3. Estimate complexity and risk level\n"
            "4. Suggest validation steps\n\n"
            "Format as a numbered list with clear, actionable items."
        )
        
        plan = await self.think(planning_prompt, f"Analysis:\n{analysis}\n\nContext:\n{context}")
        
        return {
            "plan": plan,
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def reflect_and_validate(self, plan: str, context: str) -> Dict[str, Any]:
        """
        Reflect on the plan and identify potential improvements or issues.
        
        Args:
            plan: The generated action plan
            context: Original context information
            
        Returns:
            Dictionary with reflection results
        """
        reflection_prompt = (
            "Review the following action plan and provide reflection:\n"
            "1. Identify potential risks or edge cases\n"
            "2. Suggest improvements or alternatives\n"
            "3. Highlight any missing steps\n"
            "4. Assess the likelihood of success\n\n"
            "Be critical but constructive in your evaluation."
        )
        
        reflection = await self.think(reflection_prompt, f"Plan:\n{plan}\n\nContext:\n{context}")
        
        return {
            "reflection": reflection,
            "plan": plan,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def execute_plan(self, plan: str) -> Dict[str, Any]:
        """
        Simulate plan execution (placeholder for actual tool operations).
        
        Args:
            plan: The action plan to execute
            
        Returns:
            Dictionary with execution results
        """
        # This is a placeholder for actual tool execution
        # In a full implementation, this would:
        # 1. Parse the plan for specific actions
        # 2. Execute GitHub operations (commits, PRs, etc.)
        # 3. Run tests or validations
        # 4. Handle errors and retries
        
        logger.info("Simulating plan execution...")
        
        # Simulate some processing time
        await asyncio.sleep(0.5)
        
        # For now, return a simulated successful execution
        return {
            "status": "simulated_success",
            "actions_taken": [
                "Analyzed build logs",
                "Identified configuration issue",
                "Prepared fix implementation",
                "Validated solution approach"
            ],
            "execution_time": 0.5,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def run_pipeline(self, commit_sha: str = "latest") -> Dict[str, Any]:
        """
        Full multi-step reasoning pipeline with LangGraph-style flow.
        
        Args:
            commit_sha: Commit SHA for context retrieval (default: "latest")
            
        Returns:
            Dictionary with complete pipeline results
        """
        logger.info(f"Starting LangGraph reasoning pipeline for commit: {commit_sha}")
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Retrieve context
            logger.info("Step 1: Retrieving context from FAISS store")
            context_snippets = await get_context(commit_sha, top_k=5)
            logger.info(f"Retrieved {len(context_snippets)} context snippets")
            
            # Step 2: Analyze context
            logger.info("Step 2: Analyzing context")
            analysis_result = await self.analyze_context(context_snippets)
            
            # Step 3: Plan actions
            logger.info("Step 3: Planning actions")
            plan_result = await self.plan_actions(analysis_result["analysis"], analysis_result["context_preview"])
            
            # Step 4: Send plan to Slack
            logger.info("Step 4: Sending plan notification to Slack")
            plan_summary = f"🤖 **CodeOps Agent Plan**\n\n{plan_result['plan'][:400]}..."
            self.slack.post_message(plan_summary, emoji=":brain:")
            
            # Step 5: Reflect and validate
            logger.info("Step 5: Reflecting on plan")
            reflection_result = await self.reflect_and_validate(plan_result["plan"], analysis_result["context_preview"])
            
            # Step 6: Send reflection to Slack
            logger.info("Step 6: Sending reflection notification to Slack")
            reflection_summary = f"🔍 **Plan Reflection**\n\n{reflection_result['reflection'][:400]}..."
            self.slack.post_message(reflection_summary, emoji=":mag:")
            
            # Step 7: Execute plan (simulated)
            logger.info("Step 7: Executing plan")
            execution_result = await self.execute_plan(plan_result["plan"])
            
            # Step 8: Critic review
            logger.info("Step 8: Critic review")
            critic = CriticAgent()
            critique_result = await critic.critique(
                plan_result["plan"], 
                reflection_result["reflection"],
                analysis_result["context_preview"]
            )
            
            # Record critic metrics
            from backend.app.routers.metrics import record_critic
            record_critic(critique_result.get("confidence", 0))
            
            # Step 9: Send critic review to Slack
            logger.info("Step 9: Sending critic review to Slack")
            critic_summary = critic.get_critique_summary(critique_result)
            self.slack.post_message(critic_summary, emoji=":mag_right:")
            
            # Step 10: Final summary
            end_time = datetime.utcnow()
            total_latency = (end_time - start_time).total_seconds()
            
            verdict = "success" if execution_result["status"] == "simulated_success" else "failure"
            
            logger.info(f"LangGraph reasoning completed in {total_latency:.2f}s with verdict: {verdict}")
            logger.info(f"Critic confidence: {critique_result.get('confidence', 0)}")
            
            # Send final summary to Slack
            self.slack.post_summary(verdict, self.repo_name, run_log_id=hash(commit_sha) % 10000)
            
            return {
                "verdict": verdict,
                "latency": total_latency,
                "commit_sha": commit_sha,
                "context_analysis": analysis_result,
                "action_plan": plan_result,
                "reflection": reflection_result,
                "execution": execution_result,
                "critique": critique_result,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"LangGraph pipeline error: {e}")
            
            # Send error notification to Slack
            self.slack.post_error_notification(
                f"LangGraph pipeline failed: {str(e)}",
                f"Commit: {commit_sha}, Repo: {self.repo_name}"
            )
            
            return {
                "verdict": "failure",
                "error": str(e),
                "commit_sha": commit_sha,
                "timestamp": datetime.utcnow().isoformat()
            }
