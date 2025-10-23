import asyncio
import json
import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, JSON, func, Float
from typing import Optional
from backend.app.models.run_log import RunLog
from backend.app.models.base import Base
from backend.app.retrieval import get_context
from backend.app.utils.logging import get_logger
from backend.app.agent.tools.git_tool import GitTool
from backend.app.agent.tools.test_runner_tool import TestRunnerTool
from backend.app.agent.tools.notifier_tool import NotifierTool
from backend.app.agent.github_tool import GitHubTool
from backend.app.agent.slack_tool import SlackTool
from backend.app.agent.reasoning_langgraph import LangGraphOrchestrator
from backend.app.agent.safety import check_permissions, within_token_budget


class AgentRun(Base):
    """Model for storing agent execution results."""
    __tablename__ = "agent_runs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_log_id: Mapped[int] = mapped_column(Integer, nullable=False)
    plan: Mapped[str] = mapped_column(String, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    cost_usd: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    critic_confidence: Mapped[Optional[float]] = mapped_column(Float, default=None)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AgentOrchestrator:
    """
    Orchestrator for the CodeOps Agent reasoning pipeline.
    
    Handles the full pipeline: load RunLog, retrieve context, plan fix, execute, and store results.
    """
    
    def __init__(self, db_session: AsyncSession) -> None:
        """
        Initialize the AgentOrchestrator with a database session.
        
        Args:
            db_session: Async SQLAlchemy session for database operations
        """
        self.db_session = db_session
        self.logger = get_logger(__name__)
    
    async def plan_fix(self, context_text: str) -> str:
        """
        Stub planner: produce a dummy plan string from context.
        
        Args:
            context_text: Context information as JSON string
            
        Returns:
            Plan string for fixing the issue
        """
        await asyncio.sleep(0.1)
        plan = f"Analyze logs and rerun tests based on context length {len(context_text)}"
        self.logger.info(f"plan generated: {plan}")
        return plan
    
    async def execute_plan(self, plan_text: str, repo_path: str = None, repo_name: str = "octocat/Hello-World") -> Dict[str, Any]:
        """
        Enhanced executor: run the plan with real GitHub and test operations.
        
        Args:
            plan_text: Plan to execute
            repo_path: Local repository path for test execution
            repo_name: GitHub repository name for operations
            
        Returns:
            Dictionary containing execution results
        """
        await asyncio.sleep(0.1)
        result = {"status": "ok", "details": f"Executed plan: {plan_text[:50]}..."}
        self.logger.info("plan executed successfully")
        
        # Check token budget
        tokens_used = len(plan_text.split()) * 10
        if not within_token_budget(tokens_used):
            return {"error": "token limit exceeded"}
        
        # Parse keywords from plan_text and execute appropriate tools
        tool_results = {}
        
        # GitHub operations
        if "git" in plan_text.lower() or "branch" in plan_text.lower() or "commit" in plan_text.lower():
            if check_permissions("git"):
                try:
                    github_tool = GitHubTool(repo_name)
                    
                    # Create a new branch for the fix
                    branch_name = github_tool.create_branch_with_uuid()
                    tool_results["github_branch"] = {"branch": branch_name}
                    self.logger.info(f"Created branch: {branch_name}")
                    
                    # If we have file changes to commit (this would come from the plan analysis)
                    # For now, we'll simulate this - in real implementation, this would parse the plan
                    if "fix" in plan_text.lower() or "update" in plan_text.lower():
                        # Simulate file changes - in real implementation, this would be extracted from the plan
                        file_changes = [
                            {
                                "path": "test_fix.py",
                                "content": "# Simulated fix\nprint('Fixed!')"
                            }
                        ]
                        
                        commit_sha = github_tool.commit_and_push_changes(
                            branch_name, 
                            file_changes, 
                            f"Agent fix: {plan_text[:100]}"
                        )
                        tool_results["github_commit"] = {"commit_sha": commit_sha, "branch": branch_name}
                        self.logger.info(f"Committed changes to branch {branch_name}: {commit_sha}")
                        
                except Exception as e:
                    self.logger.error(f"GitHub operations failed: {e}")
                    tool_results["github_error"] = str(e)
            else:
                self.logger.info("GitHub tool execution skipped due to safety check")
        
        # Test execution
        if "test" in plan_text.lower():
            if check_permissions("test_runner"):
                try:
                    test_tool = TestRunnerTool()
                    
                    # Use provided repo_path or default to current directory
                    test_repo_path = repo_path or "."
                    
                    # Run tests
                    test_result = await test_tool.run_tests_async(test_repo_path)
                    tool_results["test_runner"] = test_result
                    
                    # Log test results
                    if test_result["status"] == "success":
                        self.logger.info("Tests passed successfully")
                    elif test_result["status"] == "fail":
                        self.logger.warning("Tests failed")
                    else:
                        self.logger.error(f"Test execution error: {test_result.get('error', 'unknown')}")
                        
                except Exception as e:
                    self.logger.error(f"Test execution failed: {e}")
                    tool_results["test_error"] = str(e)
            else:
                self.logger.info("Test runner tool execution skipped due to safety check")
        
        # Legacy tool support
        if "notify" in plan_text.lower():
            if check_permissions("notifier"):
                notifier_tool = NotifierTool()
                tool_results["notifier"] = await notifier_tool.run()
            else:
                self.logger.info("Notifier tool execution skipped due to safety check")
        
        # Combine tool results with main result
        result.update(tool_results)
        return result
    
    async def evaluate_result(self, exec_result: dict) -> str:
        """
        Simple evaluator that checks for success or failure.
        
        Args:
            exec_result: Execution result dictionary
            
        Returns:
            Evaluation verdict ("success" or "failure")
        """
        status = exec_result.get("status", "")
        verdict = "success" if status == "ok" else "failure"
        self.logger.info(f"evaluation verdict: {verdict}")
        return verdict
    
    async def report_outcome(self, verdict: str, run_log_id: int) -> None:
        """
        Reporter that logs the outcome and notifies external systems including Slack.
        
        Args:
            verdict: Evaluation verdict
            run_log_id: ID of the RunLog that was processed
        """
        from backend.app.agent.tools.notifier_tool import NotifierTool
        from backend.app.routers.metrics import record_run
        
        # Existing notifier tool
        notifier = NotifierTool()
        message = f"Agent run {run_log_id} completed with verdict: {verdict}"
        await notifier.run(message=message)
        self.logger.info(f"report sent: {message}")
        
        # Record the run in metrics
        record_run(verdict)
        
        # Slack integration
        try:
            repo_name = "octocat/Hello-World"  # Default demo repo - can be made configurable
            slack = SlackTool()
            slack_result = slack.post_summary(verdict, repo_name, run_log_id=run_log_id)
            if slack_result.get("ok"):
                self.logger.info(f"Slack notification sent for run {run_log_id}")
            else:
                self.logger.error(f"Slack notification failed: {slack_result.get('error')}")
        except Exception as e:
            self.logger.error(f"Slack notification failed: {e}")
    
    async def github_actions(self, repo_name: str = "octocat/Hello-World"):
        """
        Fetch GitHub repository context including recent commits and workflow runs.
        
        Args:
            repo_name: GitHub repository in format "username/repo-name"
            
        Returns:
            Dictionary containing commits and workflow runs data
        """
        try:
            gh = GitHubTool(repo_name)
            commits = gh.list_recent_commits()
            workflows = gh.get_workflow_runs()
            
            self.logger.info(f"GitHub context retrieved for {repo_name}: {len(commits)} commits, {len(workflows)} workflow runs")
            return {"commits": commits, "workflows": workflows, "repo": repo_name}
        except Exception as e:
            self.logger.error(f"Error fetching GitHub context: {e}")
            return {"error": str(e), "repo": repo_name}
    
    async def run_langgraph(self, commit_sha: str = "latest", repo_name: str = "octocat/Hello-World"):
        """
        Run LangGraph-style reasoning pipeline for advanced decision-making.
        
        Args:
            commit_sha: Commit SHA for context retrieval (default: "latest")
            repo_name: GitHub repository name for context and operations
            
        Returns:
            Dictionary with LangGraph pipeline results
        """
        try:
            self.logger.info(f"Starting LangGraph reasoning for commit {commit_sha} in repo {repo_name}")
            graph = LangGraphOrchestrator(repo_name)
            result = await graph.run_pipeline(commit_sha)
            self.logger.info(f"LangGraph reasoning completed: {result.get('verdict', 'unknown')}")
            return result
        except Exception as e:
            self.logger.error(f"LangGraph reasoning failed: {e}")
            return {"error": str(e), "commit_sha": commit_sha, "repo": repo_name}
    
    async def run_pipeline(self, run_log_id: int) -> Dict[str, Any]:
        """
        Execute full pipeline: load RunLog, retrieve context, plan, execute, store result.
        
        Args:
            run_log_id: ID of the RunLog to process
            
        Returns:
            Dictionary containing pipeline execution summary
        """
        try:
            # Load RunLog
            stmt = select(RunLog).where(RunLog.id == run_log_id)
            result = await self.db_session.execute(stmt)
            run_log = result.scalar_one_or_none()
            if not run_log:
                self.logger.error(f"RunLog {run_log_id} not found")
                return {"error": "RunLog not found"}

            # Retrieve context using FAISS retrieval system
            # For now, use a mock commit SHA - in real implementation this would come from run_log
            commit_sha = f"mock_commit_{run_log_id}"
            context = await get_context(commit_sha, top_k=5)
            context_text = json.dumps(context)
            self.logger.info(f"retrieval context: {len(context)} snippets retrieved for commit {commit_sha}")

            # Plan
            plan_text = await self.plan_fix(context_text)

            # Execute with repository context
            exec_result = await self.execute_plan(plan_text, repo_path=".", repo_name="octocat/Hello-World")

            # Calculate token count and cost
            # For now, estimate tokens based on plan length (you can replace with actual token counting)
            estimated_tokens = len(plan_text.split()) * 10  # Rough estimation
            cost_per_token = 0.000002  # Example cost per token (adjust based on your LLM pricing)
            estimated_cost = estimated_tokens * cost_per_token
            
            # Store AgentRun record
            agent_run = AgentRun(
                run_log_id=run_log_id,
                plan=plan_text,
                result=exec_result,
                token_count=estimated_tokens,
                cost_usd=estimated_cost
            )
            self.db_session.add(agent_run)
            await self.db_session.commit()

            # Run critic evaluation on the results
            critic_confidence = await self.run_critic_evaluation(plan_text, exec_result)
            agent_run.critic_confidence = critic_confidence
            await self.db_session.commit()

            # Evaluate result and report outcome
            verdict = await self.evaluate_result(exec_result)
            await self.report_outcome(verdict, run_log_id)

            self.logger.info(f"Agent pipeline completed for RunLog {run_log_id}")
            return {"run_log_id": run_log_id, "plan": plan_text, "result": exec_result, "verdict": verdict}

        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            return {"error": str(e)}
    
    async def run_critic_evaluation(self, plan_text: str, exec_result: dict) -> float:
        """
        Run critic evaluation on the plan and execution results.
        
        Args:
            plan_text: The executed plan
            exec_result: The execution results
            
        Returns:
            Confidence score from 0-100
        """
        try:
            from backend.app.agent.critic_agent import CriticAgent
            
            # Create context from execution results
            context_parts = []
            
            # Add test results if available
            if "test_runner" in exec_result:
                test_result = exec_result["test_runner"]
                context_parts.append(f"Test Results: {test_result['status']}")
                if test_result.get("output"):
                    context_parts.append(f"Test Output: {test_result['output'][:500]}...")
            
            # Add GitHub operations if available
            if "github_branch" in exec_result:
                branch_info = exec_result["github_branch"]
                context_parts.append(f"Created Branch: {branch_info['branch']}")
            
            if "github_commit" in exec_result:
                commit_info = exec_result["github_commit"]
                context_parts.append(f"Commit SHA: {commit_info['commit_sha']}")
            
            # Add any errors
            if "github_error" in exec_result:
                context_parts.append(f"GitHub Error: {exec_result['github_error']}")
            
            if "test_error" in exec_result:
                context_parts.append(f"Test Error: {exec_result['test_error']}")
            
            context = "\n".join(context_parts) if context_parts else "No additional context available"
            
            # Run critic evaluation
            critic = CriticAgent()
            critique_result = await critic.quick_review(plan_text)
            
            confidence = critique_result.get("confidence", 70)
            self.logger.info(f"Critic evaluation completed with confidence: {confidence}")
            
            return float(confidence)
            
        except Exception as e:
            self.logger.error(f"Critic evaluation failed: {e}")
            return 50.0  # Default confidence on error
