from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel
import logging
import asyncio

logger = logging.getLogger(__name__)

class ConnectorConfig(BaseModel):
    """Base configuration for data connectors"""
    id: UUID
    name: str
    type: str
    credentials: Dict
    settings: Dict
    created_at: datetime
    updated_at: datetime

class DataSource(BaseModel):
    """Represents a data source in the system"""
    id: UUID
    name: str
    type: str
    connector_id: UUID
    status: str
    last_sync: Optional[datetime]
    metadata: Dict

class BaseConnector(ABC):
    """Base class for all data connectors"""
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.sources: Dict[UUID, DataSource] = {}
        self._connection = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the data source"""
        pass
        
    @abstractmethod
    async def disconnect(self):
        """Close the connection"""
        pass
        
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the connection is working"""
        pass
        
    @abstractmethod
    async def fetch_data(self, query: Dict) -> List[Dict]:
        """Fetch data from the source"""
        pass
        
    @abstractmethod
    async def write_data(self, data: List[Dict]) -> bool:
        """Write data to the source"""
        pass

class DatabaseConnector(BaseConnector):
    """Connector for database sources"""
    
    async def connect(self) -> bool:
        try:
            # In reality, would establish actual database connection
            self._connection = {
                "status": "connected",
                "timestamp": datetime.utcnow()
            }
            logger.info(f"Connected to database: {self.config.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
            
    async def disconnect(self):
        if self._connection:
            # In reality, would close actual database connection
            self._connection = None
            logger.info(f"Disconnected from database: {self.config.name}")
            
    async def test_connection(self) -> bool:
        try:
            await self.connect()
            await self.disconnect()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
            
    async def fetch_data(self, query: Dict) -> List[Dict]:
        if not self._connection:
            await self.connect()
        # In reality, would execute actual database query
        logger.info(f"Fetching data with query: {query}")
        return [{"sample": "data"}]
        
    async def write_data(self, data: List[Dict]) -> bool:
        if not self._connection:
            await self.connect()
        # In reality, would write to actual database
        logger.info(f"Writing {len(data)} records")
        return True

class APIConnector(BaseConnector):
    """Connector for REST API sources"""
    
    async def connect(self) -> bool:
        try:
            # In reality, would validate API credentials
            self._connection = {
                "status": "connected",
                "timestamp": datetime.utcnow()
            }
            logger.info(f"Connected to API: {self.config.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to API: {e}")
            return False
            
    async def disconnect(self):
        if self._connection:
            self._connection = None
            logger.info(f"Disconnected from API: {self.config.name}")
            
    async def test_connection(self) -> bool:
        try:
            await self.connect()
            await self.disconnect()
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False
            
    async def fetch_data(self, query: Dict) -> List[Dict]:
        if not self._connection:
            await self.connect()
        # In reality, would make actual API request
        logger.info(f"Fetching data from API with params: {query}")
        return [{"sample": "data"}]
        
    async def write_data(self, data: List[Dict]) -> bool:
        if not self._connection:
            await self.connect()
        # In reality, would make actual API request
        logger.info(f"Sending {len(data)} records to API")
        return True

class ConnectorRegistry:
    """Registry for managing data connectors"""
    
    def __init__(self):
        self.connectors: Dict[UUID, BaseConnector] = {}
        
    def register_connector(self, name: str, type_: str, 
                         credentials: Dict, settings: Dict) -> UUID:
        """Register a new connector"""
        config = ConnectorConfig(
            id=uuid4(),
            name=name,
            type=type_,
            credentials=credentials,
            settings=settings,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        if type_ == "database":
            connector = DatabaseConnector(config)
        elif type_ == "api":
            connector = APIConnector(config)
        else:
            raise ValueError(f"Unsupported connector type: {type_}")
            
        self.connectors[config.id] = connector
        logger.info(f"Registered new connector: {name} ({type_})")
        return config.id
        
    async def test_connector(self, connector_id: UUID) -> bool:
        """Test a connector's connection"""
        if connector_id not in self.connectors:
            raise ValueError(f"Connector {connector_id} not found")
            
        connector = self.connectors[connector_id]
        return await connector.test_connection()
        
    def get_connector(self, connector_id: UUID) -> BaseConnector:
        """Get a connector by ID"""
        if connector_id not in self.connectors:
            raise ValueError(f"Connector {connector_id} not found")
            
        return self.connectors[connector_id]
