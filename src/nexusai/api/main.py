from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, List
from uuid import UUID
import uvicorn
import logging

from ..core.orchestrator import AgentOrchestrator
from ..security.zero_trust import SecurityContext
from ..compliance.monitor import ComplianceMonitor, ComplianceLevel
from ..connectors.base import ConnectorRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NexusAI API",
    description="Enterprise AI Agent Orchestration Platform API",
    version="0.1.0"
)

# Initialize core components
orchestrator = AgentOrchestrator()
security_context = SecurityContext()
compliance_monitor = ComplianceMonitor()
connector_registry = ConnectorRegistry()

# Setup OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/agents/register")
async def register_agent(
    name: str,
    capabilities: List[str],
    security_context: Dict,
    compliance_level: str
):
    """Register a new AI agent"""
    try:
        agent = await orchestrator.register_agent(
            name=name,
            capabilities=capabilities,
            security_context=security_context,
            compliance_level=compliance_level
        )
        return {"agent_id": agent.id, "status": "registered"}
    except Exception as e:
        logger.error(f"Failed to register agent: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/tasks/submit")
async def submit_task(agent_id: UUID, input_data: Dict):
    """Submit a task for execution"""
    try:
        # Check compliance before submitting task
        violations = compliance_monitor.check_compliance(
            agent_id=agent_id,
            action={"operation": "task_submission", "data": input_data}
        )
        
        if violations:
            return {
                "status": "rejected",
                "violations": [v.dict() for v in violations]
            }
            
        task = await orchestrator.submit_task(
            agent_id=agent_id,
            input_data=input_data
        )
        return {"task_id": task.id, "status": task.status}
    except Exception as e:
        logger.error(f"Failed to submit task: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: UUID):
    """Get the current status of an agent"""
    try:
        status = await orchestrator.get_agent_status(agent_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/tasks/{task_id}/status")
async def get_task_status(task_id: UUID):
    """Get the current status of a task"""
    try:
        status = await orchestrator.get_task_status(task_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/connectors/register")
async def register_connector(
    name: str,
    type_: str,
    credentials: Dict,
    settings: Dict
):
    """Register a new data connector"""
    try:
        connector_id = connector_registry.register_connector(
            name=name,
            type_=type_,
            credentials=credentials,
            settings=settings
        )
        return {"connector_id": connector_id, "status": "registered"}
    except Exception as e:
        logger.error(f"Failed to register connector: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/compliance/rules")
async def add_compliance_rule(
    name: str,
    description: str,
    level: ComplianceLevel,
    parameters: Dict
):
    """Add a new compliance rule"""
    try:
        rule = compliance_monitor.add_rule(
            name=name,
            description=description,
            level=level,
            parameters=parameters
        )
        return {"rule_id": rule.id, "status": "created"}
    except Exception as e:
        logger.error(f"Failed to add compliance rule: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/compliance/violations")
async def get_active_violations():
    """Get all active compliance violations"""
    try:
        violations = compliance_monitor.get_active_violations()
        return {"violations": [v.dict() for v in violations]}
    except Exception as e:
        logger.error(f"Failed to get violations: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
