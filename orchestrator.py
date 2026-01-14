#!/usr/bin/env python3
"""
Orchestrator.py - Master Process for AI Employee
Monitors vault folders and automatically invokes Claude Code for autonomous task processing
"""

import os
import time
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
import schedule
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', './vault'))
NEEDS_ACTION_PATH = VAULT_PATH / 'Needs_Action'
PLANS_PATH = VAULT_PATH / 'Plans'
PENDING_APPROVAL_PATH = VAULT_PATH / 'Pending_Approval'
APPROVED_PATH = VAULT_PATH / 'Approved'
DONE_PATH = VAULT_PATH / 'Done'
LOGS_PATH = VAULT_PATH / 'Logs'

# Orchestrator settings
CHECK_INTERVAL = 30  # seconds
MAX_CONCURRENT_TASKS = 3
CLAUDE_TIMEOUT = 300  # 5 minutes max per task
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_PATH / f'orchestrator_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Orchestrator')


@dataclass
class Task:
    """Represents a task for the AI Employee"""
    id: str
    file_path: Path
    task_type: str  # email, whatsapp, file_drop, scheduled
    status: str  # pending, processing, approved, rejected, completed, failed
    created_at: str
    updated_at: str
    priority: int = 5  # 1-10, higher = more urgent
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'file_path': str(self.file_path)
        }


class TaskManager:
    """Manages task queue and state"""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.tasks: Dict[str, Task] = {}
        self.load_state()
    
    def load_state(self):
        """Load task state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    for task_data in data.get('tasks', []):
                        task_data['file_path'] = Path(task_data['file_path'])
                        task = Task(**task_data)
                        self.tasks[task.id] = task
                logger.info(f"Loaded {len(self.tasks)} tasks from state file")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
    
    def save_state(self):
        """Save task state to disk"""
        try:
            data = {
                'tasks': [task.to_dict() for task in self.tasks.values()],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def add_task(self, task: Task):
        """Add a new task"""
        self.tasks[task.id] = task
        self.save_state()
        logger.info(f"Added task: {task.id} ({task.task_type})")
    
    def update_task(self, task_id: str, **kwargs):
        """Update task properties"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.now().isoformat()
            self.save_state()
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks sorted by priority"""
        pending = [t for t in self.tasks.values() if t.status == 'pending']
        return sorted(pending, key=lambda x: (-x.priority, x.created_at))
    
    def get_task_by_file(self, file_path: Path) -> Optional[Task]:
        """Find task by file path"""
        for task in self.tasks.values():
            if task.file_path == file_path:
                return task
        return None


class ClaudeCodeExecutor:
    """Handles Claude Code invocation"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.active_processes: Dict[str, subprocess.Popen] = {}
    
    def invoke_claude(self, task: Task, prompt: str) -> bool:
        """
        Invoke Claude Code to process a task
        Returns True if successful, False otherwise
        """
        try:
            if DRY_RUN:
                logger.info(f"[DRY RUN] Would invoke Claude for task {task.id}")
                logger.info(f"[DRY RUN] Prompt: {prompt[:100]}...")
                return True
            
            # Build Claude Code command
            cmd = [
                'claude',
                '--cwd', str(self.vault_path),
                '--prompt', prompt
            ]
            
            logger.info(f"Invoking Claude Code for task {task.id}")
            
            # Execute Claude Code
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.vault_path)
            )
            
            self.active_processes[task.id] = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=CLAUDE_TIMEOUT)
                
                if process.returncode == 0:
                    logger.info(f"Claude completed task {task.id} successfully")
                    self._log_claude_output(task, stdout, stderr)
                    return True
                else:
                    logger.error(f"Claude failed for task {task.id}: {stderr}")
                    self._log_claude_output(task, stdout, stderr)
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Claude timed out for task {task.id}")
                process.kill()
                return False
            
            finally:
                if task.id in self.active_processes:
                    del self.active_processes[task.id]
        
        except Exception as e:
            logger.error(f"Failed to invoke Claude for task {task.id}: {e}")
            return False
    
    def _log_claude_output(self, task: Task, stdout: str, stderr: str):
        """Log Claude's output to a file"""
        log_file = LOGS_PATH / f'claude_output_{task.id}.log'
        try:
            with open(log_file, 'w') as f:
                f.write(f"Task: {task.id}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"\n{'='*50}\nSTDOUT:\n{'='*50}\n")
                f.write(stdout)
                f.write(f"\n{'='*50}\nSTDERR:\n{'='*50}\n")
                f.write(stderr)
        except Exception as e:
            logger.error(f"Failed to write Claude output log: {e}")
    
    def stop_all(self):
        """Stop all active Claude processes"""
        for task_id, process in self.active_processes.items():
            logger.info(f"Stopping Claude process for task {task_id}")
            process.terminate()
        self.active_processes.clear()


class VaultWatcher(FileSystemEventHandler):
    """Watches for new files in Needs_Action folder"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        super().__init__()
    
    def on_created(self, event: FileCreatedEvent):
        """Handle new file creation"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only process .md files in Needs_Action
        if file_path.suffix != '.md' or file_path.parent != NEEDS_ACTION_PATH:
            return
        
        logger.info(f"New task file detected: {file_path.name}")
        self.orchestrator.handle_new_task_file(file_path)


class Orchestrator:
    """Main orchestrator that coordinates all components"""
    
    def __init__(self):
        self.task_manager = TaskManager(VAULT_PATH / '.orchestrator_state.json')
        self.claude_executor = ClaudeCodeExecutor(VAULT_PATH)
        self.observer = Observer()
        self.running = False
        
        # Ensure all directories exist
        self._ensure_directories()
        
        # Setup file watcher
        self.observer.schedule(VaultWatcher(self), str(NEEDS_ACTION_PATH), recursive=False)
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for path in [NEEDS_ACTION_PATH, PLANS_PATH, PENDING_APPROVAL_PATH, 
                     APPROVED_PATH, DONE_PATH, LOGS_PATH]:
            path.mkdir(parents=True, exist_ok=True)
    
    def handle_new_task_file(self, file_path: Path):
        """Process a newly created task file"""
        try:
            # Read the file to extract metadata
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse task type from filename or content
            task_type = self._determine_task_type(file_path, content)
            priority = self._determine_priority(content)
            
            # Create task
            task = Task(
                id=file_path.stem,
                file_path=file_path,
                task_type=task_type,
                status='pending',
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                priority=priority
            )
            
            self.task_manager.add_task(task)
            
            # Trigger immediate processing if capacity available
            self.process_pending_tasks()
        
        except Exception as e:
            logger.error(f"Failed to handle new task file {file_path}: {e}")
    
    def _determine_task_type(self, file_path: Path, content: str) -> str:
        """Determine task type from filename or content"""
        name = file_path.name.upper()
        
        if 'EMAIL' in name:
            return 'email'
        elif 'WHATSAPP' in name:
            return 'whatsapp'
        elif 'FILE' in name:
            return 'file_drop'
        elif 'SCHEDULED' in name:
            return 'scheduled'
        
        # Check content for type hint
        if 'type: email' in content:
            return 'email'
        elif 'type: whatsapp' in content:
            return 'whatsapp'
        
        return 'unknown'
    
    def _determine_priority(self, content: str) -> int:
        """Determine task priority from content"""
        content_lower = content.lower()
        
        if 'urgent' in content_lower or 'asap' in content_lower:
            return 10
        elif 'high' in content_lower:
            return 8
        elif 'priority: high' in content_lower:
            return 8
        elif 'priority: low' in content_lower:
            return 3
        
        return 5  # default
    
    def process_pending_tasks(self):
        """Process pending tasks up to max concurrent limit"""
        pending = self.task_manager.get_pending_tasks()
        active_count = len(self.claude_executor.active_processes)
        
        if not pending:
            return
        
        logger.info(f"Processing tasks: {len(pending)} pending, {active_count} active")
        
        for task in pending[:MAX_CONCURRENT_TASKS - active_count]:
            self._process_task(task)
    
    def _process_task(self, task: Task):
        """Process a single task"""
        try:
            # Update status
            self.task_manager.update_task(task.id, status='processing')
            
            # Build prompt for Claude
            prompt = self._build_prompt(task)
            
            # Invoke Claude
            success = self.claude_executor.invoke_claude(task, prompt)
            
            if success:
                # Check if task moved to Done
                done_file = DONE_PATH / task.file_path.name
                if done_file.exists():
                    self.task_manager.update_task(task.id, status='completed')
                    logger.info(f"Task {task.id} completed successfully")
                else:
                    # Check if approval required
                    approval_files = list(PENDING_APPROVAL_PATH.glob(f'*{task.id}*'))
                    if approval_files:
                        self.task_manager.update_task(task.id, status='approved')
                        logger.info(f"Task {task.id} requires approval")
                    else:
                        # Task processed but still in Needs_Action - keep pending
                        self.task_manager.update_task(task.id, status='pending')
            else:
                # Retry logic
                if task.retry_count < task.max_retries:
                    self.task_manager.update_task(
                        task.id,
                        status='pending',
                        retry_count=task.retry_count + 1
                    )
                    logger.warning(f"Task {task.id} failed, will retry ({task.retry_count + 1}/{task.max_retries})")
                else:
                    self.task_manager.update_task(task.id, status='failed')
                    logger.error(f"Task {task.id} failed after {task.max_retries} retries")
        
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")
            self.task_manager.update_task(task.id, status='failed')
    
    def _build_prompt(self, task: Task) -> str:
        """Build the prompt for Claude based on task"""
        prompt = f"""You are an AI Employee managing tasks in an Obsidian vault.

A new task has been detected in /Needs_Action:
File: {task.file_path.name}
Type: {task.task_type}
Priority: {task.priority}

Your instructions:
1. Read the task file at {task.file_path}
2. Read the Company_Handbook.md for business rules
3. Analyze what action is required
4. Create a Plan.md file in /Plans folder with your reasoning and steps
5. If the action requires approval (payment, sensitive email), create an approval request in /Pending_Approval
6. If you can complete the action autonomously, do so following handbook rules
7. Move completed tasks to /Done folder
8. Log all actions

Remember: 
- Always follow Company_Handbook.md rules
- Flag any uncertain or high-risk actions for human approval
- Be thorough but efficient
- Update the Dashboard.md with progress

Start processing now."""
        
        return prompt
    
    def handle_approvals(self):
        """Check and process approved tasks"""
        approved_files = list(APPROVED_PATH.glob('*.md'))
        
        for file in approved_files:
            try:
                # Find the original task
                task_id = file.stem.replace('APPROVAL_', '').replace('REQUIRED_', '')
                task = self.task_manager.get_task_by_file(NEEDS_ACTION_PATH / f'{task_id}.md')
                
                if task:
                    logger.info(f"Processing approved action for task {task.id}")
                    
                    # Build approval execution prompt
                    prompt = f"""An action has been approved by the human.

Approved file: {file}
Original task: {task.file_path}

Execute the approved action now:
1. Read the approval file for details
2. Execute the action using appropriate MCP server
3. Log the action in /Logs
4. Move the approval file to /Done
5. Move the original task to /Done
6. Update Dashboard.md

Proceed with execution."""
                    
                    # Execute
                    success = self.claude_executor.invoke_claude(task, prompt)
                    
                    if success:
                        # Move approval file to Done
                        done_approval = DONE_PATH / file.name
                        file.rename(done_approval)
                        logger.info(f"Approved action executed for task {task.id}")
            
            except Exception as e:
                logger.error(f"Failed to process approval {file}: {e}")
    
    def run_scheduled_tasks(self):
        """Run scheduled tasks like CEO briefing"""
        logger.info("Running scheduled tasks check")
        
        # CEO Briefing - run every Sunday at 8 PM
        schedule.every().sunday.at("20:00").do(self.generate_ceo_briefing)
        
        # Run pending scheduled tasks
        schedule.run_pending()
    
    def generate_ceo_briefing(self):
        """Generate weekly CEO briefing"""
        logger.info("Generating CEO briefing")
        
        prompt = """Generate the weekly CEO briefing.

Follow these steps:
1. Read Business_Goals.md for objectives
2. Review all tasks in /Done from the past week
3. Check /Logs for transaction history
4. Analyze completed work, revenue, and bottlenecks
5. Generate proactive suggestions
6. Create a briefing file in /Briefings folder
7. Update Dashboard.md with briefing link

Use the CEO Briefing template from SKILL.md if available."""
        
        # Create a scheduled task
        task = Task(
            id=f"CEO_BRIEFING_{datetime.now().strftime('%Y%m%d')}",
            file_path=NEEDS_ACTION_PATH / f"SCHEDULED_CEO_BRIEFING_{datetime.now().strftime('%Y%m%d')}.md",
            task_type='scheduled',
            status='pending',
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            priority=7
        )
        
        # Create placeholder file
        task.file_path.write_text(f"""---
type: scheduled
task: ceo_briefing
priority: high
---

Generate weekly CEO briefing for {datetime.now().strftime('%Y-%m-%d')}
""")
        
        self.task_manager.add_task(task)
    
    def start(self):
        """Start the orchestrator"""
        logger.info("=" * 60)
        logger.info("AI EMPLOYEE ORCHESTRATOR STARTING")
        logger.info("=" * 60)
        logger.info(f"Vault path: {VAULT_PATH}")
        logger.info(f"Dry run mode: {DRY_RUN}")
        logger.info(f"Max concurrent tasks: {MAX_CONCURRENT_TASKS}")
        
        self.running = True
        
        # Start file watcher
        self.observer.start()
        logger.info("File watcher started")
        
        # Process any existing pending tasks
        existing_files = list(NEEDS_ACTION_PATH.glob('*.md'))
        if existing_files:
            logger.info(f"Found {len(existing_files)} existing task files")
            for file in existing_files:
                if not self.task_manager.get_task_by_file(file):
                    self.handle_new_task_file(file)
        
        try:
            while self.running:
                # Process pending tasks
                self.process_pending_tasks()
                
                # Check for approvals
                self.handle_approvals()
                
                # Run scheduled tasks
                self.run_scheduled_tasks()
                
                # Sleep between cycles
                time.sleep(CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the orchestrator"""
        logger.info("Shutting down orchestrator...")
        self.running = False
        
        # Stop file watcher
        self.observer.stop()
        self.observer.join()
        
        # Stop Claude processes
        self.claude_executor.stop_all()
        
        # Save final state
        self.task_manager.save_state()
        
        logger.info("Orchestrator stopped")


def main():
    """Main entry point"""
    orchestrator = Orchestrator()
    orchestrator.start()


if __name__ == '__main__':
    main()
