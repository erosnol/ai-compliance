import pytest
import asyncio
from uuid import UUID
from datetime import datetime
from src.nexusai.core.orchestrator import AgentOrchestrator

@pytest.fixture
def orchestrator():
    return AgentOrchestrator()

@pytest.mark.asyncio
async def test_register_agent(orchestrator):
    # Test agent registration
    agent = await orchestrator.register_agent(
        name="test_agent",
        capabilities=["text_processing", "data_analysis"],
        security_context={"role": "test"},
        compliance_level="HIGH"
    )
    
    assert isinstance(agent.id, UUID)
    assert agent.name == "test_agent"
    assert agent.status == "READY"
    assert len(agent.capabilities) == 2
    assert agent.compliance_level == "HIGH"

@pytest.mark.asyncio
async def test_submit_task(orchestrator):
    # First register an agent
    agent = await orchestrator.register_agent(
        name="test_agent",
        capabilities=["text_processing"],
        security_context={"role": "test"},
        compliance_level="HIGH"
    )
    
    # Submit a task
    task = await orchestrator.submit_task(
        agent_id=agent.id,
        input_data={"text": "Test input"}
    )
    
    assert isinstance(task.id, UUID)
    assert task.agent_id == agent.id
    assert task.status == "PENDING"
    assert task.input_data == {"text": "Test input"}

@pytest.mark.asyncio
async def test_get_agent_status(orchestrator):
    # Register an agent
    agent = await orchestrator.register_agent(
        name="test_agent",
        capabilities=["text_processing"],
        security_context={"role": "test"},
        compliance_level="HIGH"
    )
    
    # Get status
    status = await orchestrator.get_agent_status(agent.id)
    
    assert status["id"] == agent.id
    assert status["name"] == "test_agent"
    assert status["status"] == "READY"
    assert status["compliance_level"] == "HIGH"

@pytest.mark.asyncio
async def test_get_task_status(orchestrator):
    # Register an agent
    agent = await orchestrator.register_agent(
        name="test_agent",
        capabilities=["text_processing"],
        security_context={"role": "test"},
        compliance_level="HIGH"
    )
    
    # Submit a task
    task = await orchestrator.submit_task(
        agent_id=agent.id,
        input_data={"text": "Test input"}
    )
    
    # Get status
    status = await orchestrator.get_task_status(task.id)
    
    assert status["id"] == task.id
    assert status["agent_id"] == agent.id
    assert status["status"] in ["PENDING", "PROCESSING"]
    assert isinstance(status["created_at"], datetime)
    assert isinstance(status["updated_at"], datetime)
