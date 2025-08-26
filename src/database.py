"""
Database utilities for the crypto data pipeline.
"""

import logging
from typing import Optional, Dict, Any, Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from clickhouse_driver import Client as ClickHouseClient

from config import current_config

# Setup logging
logging.basicConfig(level=current_config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# SQLAlchemy base
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.postgres_engine = None
        self.postgres_session_factory = None
        self.clickhouse_client = None
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize database connections."""
        try:
            # PostgreSQL connection
            self.postgres_engine = create_engine(
                current_config.get_postgres_url(),
                echo=current_config.DEBUG,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            self.postgres_session_factory = sessionmaker(bind=self.postgres_engine)
            logger.info("PostgreSQL connection initialized successfully")
            
            # ClickHouse connection
            clickhouse_config = current_config.CLICKHOUSE_CONFIG
            self.clickhouse_client = ClickHouseClient(
                host=clickhouse_config['host'],
                port=clickhouse_config['port'],
                database=clickhouse_config['database']
            )
            logger.info("ClickHouse connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise
    
    @contextmanager
    def get_postgres_session(self) -> Generator[Session, None, None]:
        """Get PostgreSQL session with context manager."""
        session = self.postgres_session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def execute_postgres_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a PostgreSQL query."""
        try:
            with self.get_postgres_session() as session:
                result = session.execute(text(query), params or {})
                return result.fetchall()
        except Exception as e:
            logger.error(f"Failed to execute PostgreSQL query: {e}")
            raise
    
    def execute_clickhouse_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a ClickHouse query."""
        try:
            return self.clickhouse_client.execute(query, params or {})
        except Exception as e:
            logger.error(f"Failed to execute ClickHouse query: {e}")
            raise
    
    def test_connections(self) -> Dict[str, bool]:
        """Test all database connections."""
        results = {}
        
        # Test PostgreSQL
        try:
            with self.get_postgres_session() as session:
                session.execute(text("SELECT 1"))
            results['postgres'] = True
            logger.info("PostgreSQL connection test: SUCCESS")
        except Exception as e:
            results['postgres'] = False
            logger.error(f"PostgreSQL connection test: FAILED - {e}")
        
        # Test ClickHouse
        try:
            self.clickhouse_client.execute("SELECT 1")
            results['clickhouse'] = True
            logger.info("ClickHouse connection test: SUCCESS")
        except Exception as e:
            results['clickhouse'] = False
            logger.error(f"ClickHouse connection test: FAILED - {e}")
        
        return results


# Global database manager instance
db_manager = DatabaseManager()
