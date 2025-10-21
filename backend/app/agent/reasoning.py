import asyncio
import json
import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, JSON, func
from backend.app.models.run_log import RunLog
from backend.app.models.base import Base
from backend.app.retrieval.context import ContextRetriever
from backend.app.utils.logging import get_logger
from backend.app.agent.tools.git_tool import GitTool
from backend.app.agent.tools.test_runner_tool import TestRunnerTool
from backend.app.agent.tools.notifier_tool import NotifierTool
from backend.app.agent.safety import check_permissions, within_token_budget


class AgentRun(Base):
    """Model for storing agent execution results."""
    __tablename__ = "agent_runs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_log_id: Mapped[int] = mapped_column(Integer, nullable=False)
    plan: Mapped[str] = mapped_column(String, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
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
    
    async def execute_plan(self, plan_text: str) -> Dict[str, Any]:
        """
        Stub executor: simulate running the plan.
        
        Args:
            plan_text: Plan to execute
            
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
        
        if "git" in plan_text.lower():
            if check_permissions("git"):
                git_tool = GitTool()
                tool_results["git"] = await git_tool.run()
            else:
                self.logger.info("Git tool execution skipped due to safety check")
        
        if "test" in plan_text.lower():
            if check_permissions("test_runner"):
                test_tool = TestRunnerTool()
                tool_results["test_runner"] = await test_tool.run()
            else:
                self.logger.info("Test runner tool execution skipped due to safety check")
        
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
        Stub reporter that logs the outcome and notifies external systems.
        
        Args:
            verdict: Evaluation verdict
            run_log_id: ID of the RunLog that was processed
        """
        from backend.app.agent.tools.notifier_tool import NotifierTool
        from backend.app.routers.metrics import record_run
        
        notifier = NotifierTool()
        message = f"Agent run {run_log_id} completed with verdict: {verdict}"
        await notifier.run(message=message)
        self.logger.info(f"report sent: {message}")
        
        # Record the run in metrics
        record_run(verdict)
    
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

            # Retrieve context
            retriever = ContextRetriever(self.db_session)
            await retriever.build_context_index()
            context = await retriever.query_context("build failure diagnostics")
            context_text = json.dumps(context)

            # Plan
            plan_text = await self.plan_fix(context_text)

            # Execute
            exec_result = await self.execute_plan(plan_text)

            # Store AgentRun record
            agent_run = AgentRun(
                run_log_id=run_log_id,
                plan=plan_text,
                result=exec_result
            )
            self.db_session.add(agent_run)
            await self.db_session.commit()

            # Evaluate result and report outcome
            verdict = await self.evaluate_result(exec_result)
            await self.report_outcome(verdict, run_log_id)

            self.logger.info(f"Agent pipeline completed for RunLog {run_log_id}")
            return {"run_log_id": run_log_id, "plan": plan_text, "result": exec_result, "verdict": verdict}

        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            return {"error": str(e)}
