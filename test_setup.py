#!/usr/bin/env python3
"""
Test script to verify the Semantic Kernel Agent 2 Agent setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if all required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_API_VERSION"
    ]
    
    print("🔍 Testing Environment Configuration...")
    print("-" * 40)
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_"):
            missing_vars.append(var)
            print(f"❌ {var}: Not configured")
        else:
            # Hide sensitive values
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {display_value}")
    
    if missing_vars:
        print("\n⚠️  Please configure the following variables in .env file:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("\n✅ All environment variables are configured!")
    return True

def test_imports():
    """Test if all required packages are installed"""
    print("\n🔍 Testing Package Imports...")
    print("-" * 40)
    
    try:
        import semantic_kernel
        print(f"✅ semantic-kernel: {semantic_kernel.__version__}")
    except ImportError as e:
        print(f"❌ semantic-kernel: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()  # Test the function
        print("✅ python-dotenv: Available")
    except ImportError as e:
        print(f"❌ python-dotenv: {e}")
        return False
    
    try:
        import openai
        print(f"✅ openai: {openai.__version__}")
    except ImportError as e:
        print(f"❌ openai: {e}")
        return False
    
    print("\n✅ All packages are installed!")
    return True

def main():
    """Main test function"""
    print("🤖 Semantic Kernel Agent 2 Agent - Setup Test")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import test failed. Please install required packages:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Test environment
    if not test_environment():
        print("\n❌ Environment test failed. Please configure your .env file.")
        sys.exit(1)
    
    print("\n🎉 Setup test completed successfully!")
    print("You can now run the main application:")
    print("   python main.py")

if __name__ == "__main__":
    main()
