import subprocess
import os
import asyncio
from typing import Dict, Any
from backend.app.utils.logging import get_logger
from backend.app.config import settings
from backend.app.agent.safety import (
    validate_repo_path,
    log_operation,
    is_dry_run_mode
)


class TestRunnerTool:
    """Real test runner tool for executing tests safely."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def run(self, tests: str = "pytest") -> dict:
        """
        Stub test runner for backward compatibility.
        
        Args:
            tests: Test command to execute
            
        Returns:
            Dictionary containing tool execution results
        """
        self.logger.info(f"TestRunnerTool: executed {tests}")
        return {"tool": "test_runner", "tests": tests, "status": "ok"}
    
    def run_tests(self, repo_path: str, test_command: str = "pytest -q") -> Dict[str, Any]:
        """
        Run tests in a repository safely.
        
        Args:
            repo_path: Path to the repository
            test_command: Test command to execute (default: "pytest -q")
            
        Returns:
            Dictionary with test results including status, output, and metadata
        """
        try:
            # Safety check: validate repository path
            if not validate_repo_path(repo_path):
                return {
                    "status": "error",
                    "output": f"Invalid or unsafe repository path: {repo_path}",
                    "error": "invalid_path"
                }
            
            # Check if we're in dry run mode
            if is_dry_run_mode():
                self.logger.info(f"DRY RUN: Would execute '{test_command}' in {repo_path}")
                return {
                    "status": "dry_run",
                    "output": f"DRY RUN: Would execute '{test_command}' in {repo_path}",
                    "command": test_command,
                    "path": repo_path
                }
            
            # Log the operation
            log_operation("Run_Tests", {
                "command": test_command,
                "path": repo_path
            })
            
            # Activate virtual environment if it exists
            venv_path = os.path.join(repo_path, ".venv")
            if os.path.exists(venv_path):
                # On Windows, use Scripts\activate.bat, on Unix use bin/activate
                if os.name == 'nt':  # Windows
                    activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
                    if os.path.exists(activate_script):
                        # For Windows, we need to use cmd /c to run the batch file
                        full_command = f'cmd /c "{activate_script} && {test_command}"'
                    else:
                        full_command = test_command
                else:  # Unix/Linux/Mac
                    activate_script = os.path.join(venv_path, "bin", "activate")
                    if os.path.exists(activate_script):
                        full_command = f"source {activate_script} && {test_command}"
                    else:
                        full_command = test_command
            else:
                full_command = test_command
            
            self.logger.info(f"Running tests: {full_command} in {repo_path}")
            
            # Execute the test command
            result = subprocess.run(
                full_command,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                shell=True
            )
            
            # Determine status
            if result.returncode == 0:
                status = "success"
            else:
                status = "fail"
            
            output = result.stdout + result.stderr
            
            self.logger.info(f"Test execution completed with status: {status}")
            
            return {
                "status": status,
                "output": output,
                "return_code": result.returncode,
                "command": full_command,
                "path": repo_path,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Test execution timed out after 5 minutes")
            return {
                "status": "timeout",
                "output": "Test execution timed out after 5 minutes",
                "error": "timeout"
            }
        except Exception as e:
            self.logger.error(f"Error running tests: {e}")
            return {
                "status": "error",
                "output": str(e),
                "error": "execution_error"
            }
    
    async def run_tests_async(self, repo_path: str, test_command: str = "pytest -q") -> Dict[str, Any]:
        """
        Async wrapper for run_tests.
        
        Args:
            repo_path: Path to the repository
            test_command: Test command to execute
            
        Returns:
            Dictionary with test results
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run_tests, repo_path, test_command)
