"""
Simplified setup and testing script for the crypto data pipeline.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import current_config


def test_configuration():
    """Test the configuration setup."""
    print("🔧 Testing Configuration...")
    print(f"Environment: {current_config.ENVIRONMENT}")
    print(f"PostgreSQL URL: {current_config.get_postgres_url()}")
    print(f"Data Collection Interval: {current_config.DATA_COLLECTION_INTERVAL}s")
    print(f"Top Cryptocurrencies: {current_config.TOP_CRYPTOCURRENCIES}")
    print("✅ Configuration loaded successfully\n")


def main():
    """Main setup and testing function."""
    print("🚀 Crypto Data Pipeline - Initial Setup\n")
    
    # Test configuration
    test_configuration()
    
    print("🎉 Basic setup completed! Next steps:")
    print("1. Copy .env.example to .env and configure your API keys")
    print("2. Install remaining dependencies: pip install -r requirements.txt")
    print("3. Run 'docker-compose up -d' to start services")
    print("4. Access Airflow at http://localhost:8080")
    print("5. Access Grafana at http://localhost:3000")


if __name__ == "__main__":
    main()
