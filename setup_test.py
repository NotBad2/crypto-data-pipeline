"""
Initial setup and testing script for the crypto data pipeline.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import current_config
from database import db_manager


def test_configuration():
    """Test the configuration setup."""
    print("🔧 Testing Configuration...")
    print(f"Environment: {current_config.ENVIRONMENT}")
    print(f"PostgreSQL URL: {current_config.get_postgres_url()}")
    print(f"ClickHouse Config: {current_config.CLICKHOUSE_CONFIG}")
    print(f"Data Collection Interval: {current_config.DATA_COLLECTION_INTERVAL}s")
    print(f"Top Cryptocurrencies: {current_config.TOP_CRYPTOCURRENCIES}")
    print("✅ Configuration loaded successfully\n")


def test_database_connections():
    """Test database connections."""
    print("🗄️ Testing Database Connections...")
    
    try:
        results = db_manager.test_connections()
        
        for db_name, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {db_name.capitalize()}: {'Connected' if status else 'Failed'}")
        
        if all(results.values()):
            print("✅ All database connections successful\n")
            return True
        else:
            print("❌ Some database connections failed\n")
            return False
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}\n")
        return False


def main():
    """Main setup and testing function."""
    print("🚀 Crypto Data Pipeline - Initial Setup\n")
    
    # Test configuration
    test_configuration()
    
    # Test database connections (will fail until Docker is running)
    print("Note: Database connection tests will fail until Docker services are running.")
    print("Run 'docker-compose up -d' to start the services first.\n")
    
    test_database_connections()
    
    print("🎉 Setup completed! Next steps:")
    print("1. Copy .env.example to .env and configure your API keys")
    print("2. Run 'docker-compose up -d' to start services")
    print("3. Access Airflow at http://localhost:8080")
    print("4. Access Grafana at http://localhost:3000")


if __name__ == "__main__":
    main()
