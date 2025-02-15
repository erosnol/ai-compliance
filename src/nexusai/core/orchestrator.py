from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, UTC
from pydantic import BaseModel
import asyncio
import logging

logger = logging.getLogger(__name__)

class Agent(BaseModel):
    """Represents an AI agent in the system"""
    id: UUID
    name: str
    capabilities: List[str]
    status: str
    created_at: datetime
    last_active: datetime
    security_context: Dict
    compliance_level: str

class Task(BaseModel):
    """Represents a task that can be executed by agents"""
    id: UUID
    agent_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    input_data: Dict
    output_data: Optional[Dict]
    error: Optional[str]

class AgentOrchestrator:
    """Core orchestration engine for managing AI agents"""
    
    def __init__(self):
        self.agents: Dict[UUID, Agent] = {}
        self.tasks: Dict[UUID, Task] = {}
        self._task_queue = asyncio.Queue()
        
    async def register_agent(self, name: str, capabilities: List[str], 
                           security_context: Dict, compliance_level: str) -> Agent:
        """Register a new agent with the orchestrator"""
        agent = Agent(
            id=uuid4(),
            name=name,
            capabilities=capabilities,
            status="READY",
            created_at=datetime.now(UTC),
            last_active=datetime.now(UTC),
            security_context=security_context,
            compliance_level=compliance_level
        )
        self.agents[agent.id] = agent
        logger.info(f"Registered new agent: {agent.name} with ID: {agent.id}")
        return agent

    async def submit_task(self, agent_id: UUID, input_data: Dict) -> Task:
        """Submit a new task for execution"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
            
        task = Task(
            id=uuid4(),
            agent_id=agent_id,
            status="PENDING",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            input_data=input_data,
            output_data=None,
            error=None
        )
        self.tasks[task.id] = task
        await self._task_queue.put(task)
        logger.info(f"Submitted task {task.id} for agent {agent_id}")
        return task

    async def process_tasks(self):
        """Main task processing loop"""
        while True:
            task = await self._task_queue.get()
            try:
                # Update task status
                task.status = "PROCESSING"
                task.updated_at = datetime.utcnow()
                
                # Update agent status
                agent = self.agents[task.agent_id]
                agent.status = "BUSY"
                agent.last_active = datetime.utcnow()
                
                # Here we would integrate with actual agent execution
                # For now, we'll just log the task
                logger.info(f"Processing task {task.id} for agent {agent.name}")
                
                # Update task completion
                task.status = "COMPLETED"
                task.updated_at = datetime.utcnow()
                agent.status = "READY"
                
            except Exception as e:
                task.status = "FAILED"
                task.error = str(e)
                logger.error(f"Task {task.id} failed: {e}")
            finally:
                self._task_queue.task_done()

    async def get_agent_status(self, agent_id: UUID) -> Dict:
        """Get the current status of an agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
            
        agent = self.agents[agent_id]
        return {
            "id": agent.id,
            "name": agent.name,
            "status": agent.status,
            "last_active": agent.last_active,
            "compliance_level": agent.compliance_level
        }

    async def get_task_status(self, task_id: UUID) -> Dict:
        """Get the current status of a task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
            
        task = self.tasks[task_id]
        return {
            "id": task.id,
            "agent_id": task.agent_id,
            "status": task.status,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "error": task.error
        }
