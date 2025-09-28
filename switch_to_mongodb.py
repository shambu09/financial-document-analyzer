#!/usr/bin/env python3
"""
Script to switch the application from SQLite to MongoDB
This demonstrates how easy it is to switch database types with the new architecture
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.factory import ModelManager
from app.config import DatabaseConfig


def test_database_switch():
    """Test switching between SQLite and MongoDB"""
    
    print("🔄 Testing Database Switch...")
    print("=" * 50)
    
    # Test SQLite
    print("\n📁 Testing SQLite...")
    try:
        sqlite_manager = ModelManager("sqlite", db_path="test_sqlite.db")
        user_model = sqlite_manager.get_user_model()
        print("✅ SQLite connection successful")
        
        # Test creating a user
        user_id = user_model.create_user("test_user", "test@example.com", "password123")
        print(f"✅ SQLite user created with ID: {user_id}")
        
        # Clean up
        sqlite_manager.close()
        os.remove("test_sqlite.db")
        print("✅ SQLite test completed and cleaned up")
        
    except Exception as e:
        print(f"❌ SQLite test failed: {str(e)}")
    
    # Test MongoDB
    print("\n🍃 Testing MongoDB...")
    try:
        mongodb_manager = ModelManager(
            "mongodb", 
            connection_string="mongodb://localhost:27017",
            database_name="test_financial_analyzer"
        )
        user_model = mongodb_manager.get_user_model()
        print("✅ MongoDB connection successful")
        
        # Test creating a user
        user_id = user_model.create_user("test_user_mongo", "test_mongo@example.com", "password123")
        print(f"✅ MongoDB user created with ID: {user_id}")
        
        # Test retrieving the user
        user_data = user_model.get_user_by_id(user_id)
        if user_data:
            print(f"✅ MongoDB user retrieved: {user_data['username']}")
        
        # Clean up
        mongodb_manager.close()
        print("✅ MongoDB test completed")
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {str(e)}")
        print("💡 Make sure MongoDB is running: docker run -d -p 27017:27017 mongo")


def show_environment_setup():
    """Show how to set up environment variables for MongoDB"""
    
    print("\n🔧 Environment Setup for MongoDB")
    print("=" * 50)
    
    print("\n1. Set environment variables:")
    print("   export DATABASE_TYPE=mongodb")
    print("   export MONGODB_CONNECTION_STRING=mongodb://localhost:27017")
    print("   export MONGODB_DATABASE_NAME=financial_analyzer")
    
    print("\n2. Or create a .env file:")
    print("   DATABASE_TYPE=mongodb")
    print("   MONGODB_CONNECTION_STRING=mongodb://localhost:27017")
    print("   MONGODB_DATABASE_NAME=financial_analyzer")
    
    print("\n3. Start MongoDB:")
    print("   # Using Docker:")
    print("   docker run -d -p 27017:27017 --name mongodb mongo")
    print("   # Or install MongoDB locally")
    
    print("\n4. Run the application:")
    print("   uvicorn main:app --reload")


def show_code_examples():
    """Show code examples for using different databases"""
    
    print("\n💻 Code Examples")
    print("=" * 50)
    
    print("\n# Using SQLite (default)")
    print("from app.models.factory import get_user_model")
    print("user_model = get_user_model()  # Uses SQLite by default")
    
    print("\n# Using MongoDB")
    print("from app.models.factory import ModelManager")
    print("manager = ModelManager('mongodb', connection_string='mongodb://localhost:27017')")
    print("user_model = manager.get_user_model()")
    
    print("\n# Using configuration")
    print("from app.config import DatabaseConfig")
    print("config = DatabaseConfig.get_database_config()")
    print("manager = ModelManager(config['db_type'], **config)")


if __name__ == "__main__":
    print("🚀 Database Switch Demo")
    print("=" * 50)
    
    # Show current configuration
    try:
        config = DatabaseConfig.get_database_config()
        print(f"Current database type: {config['db_type']}")
    except Exception as e:
        print(f"Configuration error: {e}")
    
    # Test database switching
    test_database_switch()
    
    # Show setup instructions
    show_environment_setup()
    
    # Show code examples
    show_code_examples()
    
    print("\n✨ That's it! The architecture makes switching databases trivial!")
