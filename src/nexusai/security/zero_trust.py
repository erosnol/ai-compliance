from typing import Dict, Optional
from datetime import datetime, timedelta
from uuid import UUID
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

class SecurityContext:
    """Manages security context for zero-trust architecture"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # In production, these would be loaded from secure environment variables
        self.SECRET_KEY = "your-secret-key"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict:
        """Verify a JWT token"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError("Could not validate credentials")

class AgentSandbox:
    """Provides isolated execution environment for agents"""
    
    def __init__(self, agent_id: UUID):
        self.agent_id = agent_id
        self.allowed_operations = set()
        self.resource_limits = {}
        self.audit_log = []
        
    def add_allowed_operation(self, operation: str):
        """Add an allowed operation to the sandbox"""
        self.allowed_operations.add(operation)
        
    def set_resource_limits(self, cpu_percent: float, memory_mb: int, 
                          network_calls_per_minute: int):
        """Set resource limits for the sandbox"""
        self.resource_limits = {
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb,
            "network_calls_per_minute": network_calls_per_minute
        }
        
    def verify_operation(self, operation: str) -> bool:
        """Verify if an operation is allowed in the sandbox"""
        return operation in self.allowed_operations
        
    def log_operation(self, operation: str, timestamp: datetime, 
                     success: bool, details: Dict):
        """Log an operation for audit purposes"""
        log_entry = {
            "agent_id": self.agent_id,
            "operation": operation,
            "timestamp": timestamp,
            "success": success,
            "details": details
        }
        self.audit_log.append(log_entry)
        logger.info(f"Logged operation: {operation} for agent {self.agent_id}")

class DataEncryption:
    """Handles data encryption for sensitive information"""
    
    @staticmethod
    def encrypt_data(data: Dict, encryption_key: str) -> Dict:
        """Encrypt sensitive data"""
        # In a real implementation, this would use proper encryption
        # For now, we'll just mark it as encrypted
        return {
            "encrypted": True,
            "data": str(data)  # In reality, this would be encrypted
        }
        
    @staticmethod
    def decrypt_data(encrypted_data: Dict, encryption_key: str) -> Dict:
        """Decrypt sensitive data"""
        # In a real implementation, this would use proper decryption
        if not encrypted_data.get("encrypted"):
            raise ValueError("Data is not encrypted")
        # In reality, this would be decrypted
        return {"decrypted": True, "data": encrypted_data["data"]}
