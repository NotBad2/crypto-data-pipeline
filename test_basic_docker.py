"""
Simple test for basic Docker services.
"""

import requests
import time
import sys

def test_postgres():
    """Test PostgreSQL connection."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="crypto_data",
            user="crypto_user",
            password="crypto_pass"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL: {version.split(',')[0]}")
        cursor.close()
        conn.close()
        return True
    except ImportError:
        print("⚠️ psycopg2 not installed, installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        return test_postgres()
    except Exception as e:
        print(f"❌ PostgreSQL: {e}")
        return False

def test_clickhouse():
    """Test ClickHouse connection."""
    try:
        response = requests.get("http://localhost:8123/", timeout=10)
        if response.status_code == 200 and "Ok." in response.text:
            print("✅ ClickHouse: HTTP interface accessible")
            return True
        else:
            print(f"❌ ClickHouse: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ClickHouse: {e}")
        return False

def test_redis():
    """Test Redis connection."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379)
        if r.ping():
            print("✅ Redis: Responding to ping")
            return True
        else:
            print("❌ Redis: Not responding")
            return False
    except ImportError:
        print("⚠️ redis not installed, installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "redis"])
        return test_redis()
    except Exception as e:
        print(f"❌ Redis: {e}")
        return False

def test_grafana():
    """Test Grafana connection."""
    try:
        response = requests.get("http://localhost:3000/", timeout=10)
        if response.status_code == 200:
            print("✅ Grafana: Web interface accessible")
            return True
        else:
            print(f"❌ Grafana: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Grafana: {e}")
        return False

def main():
    print("🐳 Testing Basic Docker Services")
    print("=" * 40)
    
    # Wait for services to be ready
    print("⏳ Waiting for services...")
    time.sleep(5)
    
    tests = [
        ("PostgreSQL", test_postgres),
        ("ClickHouse", test_clickhouse), 
        ("Redis", test_redis),
        ("Grafana", test_grafana)
    ]
    
    passed = 0
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name}: Test crashed - {e}")
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{len(tests)} services working")
    
    if passed == len(tests):
        print("🎉 All basic services are running!")
        print("\n🔗 Service URLs:")
        print("   📊 Grafana:    http://localhost:3000 (admin/admin)")
        print("   🗄️ PostgreSQL: localhost:5432 (crypto_user/crypto_pass)")
        print("   ⚡ ClickHouse: http://localhost:8123")
        print("   🔴 Redis:      localhost:6379")
    else:
        print("⚠️ Some services have issues. Check Docker logs.")

if __name__ == "__main__":
    main()
