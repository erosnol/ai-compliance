from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ComplianceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ComplianceRule(BaseModel):
    """Represents a compliance rule"""
    id: UUID
    name: str
    description: str
    level: ComplianceLevel
    parameters: Dict
    created_at: datetime
    updated_at: datetime

class ComplianceViolation(BaseModel):
    """Represents a compliance violation"""
    id: UUID
    rule_id: UUID
    agent_id: UUID
    timestamp: datetime
    details: Dict
    status: str  # OPEN, RESOLVED, IGNORED
    resolution: Optional[str]

class ComplianceMonitor:
    """Monitors and enforces compliance rules"""
    
    def __init__(self):
        self.rules: Dict[UUID, ComplianceRule] = {}
        self.violations: Dict[UUID, ComplianceViolation] = {}
        
    def add_rule(self, name: str, description: str, level: ComplianceLevel, 
                parameters: Dict) -> ComplianceRule:
        """Add a new compliance rule"""
        rule = ComplianceRule(
            id=UUID(int=len(self.rules) + 1),
            name=name,
            description=description,
            level=level,
            parameters=parameters,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.rules[rule.id] = rule
        logger.info(f"Added compliance rule: {rule.name}")
        return rule
        
    def check_compliance(self, agent_id: UUID, action: Dict) -> List[ComplianceViolation]:
        """Check an action against compliance rules"""
        violations = []
        
        for rule in self.rules.values():
            # Example compliance checks based on rule parameters
            if rule.parameters.get("restricted_operations"):
                if action.get("operation") in rule.parameters["restricted_operations"]:
                    violation = ComplianceViolation(
                        id=UUID(int=len(self.violations) + 1),
                        rule_id=rule.id,
                        agent_id=agent_id,
                        timestamp=datetime.utcnow(),
                        details={
                            "action": action,
                            "violation_type": "restricted_operation",
                            "operation": action.get("operation")
                        },
                        status="OPEN",
                        resolution=None
                    )
                    self.violations[violation.id] = violation
                    violations.append(violation)
                    logger.warning(f"Compliance violation detected: {violation.details}")
                    
            if rule.parameters.get("data_sensitivity"):
                if action.get("data_classification", "LOW") == "HIGH" and \
                   rule.parameters["data_sensitivity"] == "restricted":
                    violation = ComplianceViolation(
                        id=UUID(int=len(self.violations) + 1),
                        rule_id=rule.id,
                        agent_id=agent_id,
                        timestamp=datetime.utcnow(),
                        details={
                            "action": action,
                            "violation_type": "data_sensitivity",
                            "classification": action.get("data_classification")
                        },
                        status="OPEN",
                        resolution=None
                    )
                    self.violations[violation.id] = violation
                    violations.append(violation)
                    logger.warning(f"Compliance violation detected: {violation.details}")
        
        return violations
        
    def resolve_violation(self, violation_id: UUID, resolution: str):
        """Resolve a compliance violation"""
        if violation_id not in self.violations:
            raise ValueError(f"Violation {violation_id} not found")
            
        violation = self.violations[violation_id]
        violation.status = "RESOLVED"
        violation.resolution = resolution
        logger.info(f"Resolved compliance violation: {violation_id}")
        
    def get_violations_by_agent(self, agent_id: UUID) -> List[ComplianceViolation]:
        """Get all violations for a specific agent"""
        return [v for v in self.violations.values() if v.agent_id == agent_id]
        
    def get_active_violations(self) -> List[ComplianceViolation]:
        """Get all active (unresolved) violations"""
        return [v for v in self.violations.values() if v.status == "OPEN"]

class ComplianceReport(BaseModel):
    """Generates compliance reports"""
    
    @staticmethod
    def generate_summary(violations: List[ComplianceViolation]) -> Dict:
        """Generate a summary report of compliance violations"""
        summary = {
            "total_violations": len(violations),
            "open_violations": len([v for v in violations if v.status == "OPEN"]),
            "resolved_violations": len([v for v in violations if v.status == "RESOLVED"]),
            "by_level": {},
            "timestamp": datetime.utcnow()
        }
        
        # Group violations by compliance level
        for violation in violations:
            level = violation.rule_id  # In reality, would look up rule level
            if level not in summary["by_level"]:
                summary["by_level"][level] = 0
            summary["by_level"][level] += 1
            
        return summary
