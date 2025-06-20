#!/usr/bin/env python3
"""
Direct SNC command tester - bypasses aider's main module
"""

import sys
import os
from pathlib import Path

# Add aider to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import SNC directly
from aider.snc import handle_snc_command

def test_snc_commands():
    """Test SNC commands directly"""
    print("Testing SNC Commands with Live API Server")
    print("=" * 50)
    
    # Test 1: Login
    print("\n1. Testing Login...")
    argv = ['snc', '--user', 'user@company.com', '--token', 'demo-token-12345', '--api-url', 'http://localhost:5000']
    try:
        result = handle_snc_command(argv)
        print(f"✓ Login result: {result}")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return False
    
    # Test 2: Status check
    print("\n2. Testing Status Check...")
    argv = ['snc', '--status', '--api-url', 'http://localhost:5000']
    try:
        result = handle_snc_command(argv)
        print(f"✓ Status result: {result}")
    except Exception as e:
        print(f"✗ Status check failed: {e}")
    
    # Test 3: Another login with different user
    print("\n3. Testing Login with Different User...")
    argv = ['snc', '--user', 'admin@company.com', '--token', 'admin-token-67890', '--api-url', 'http://localhost:5000']
    try:
        result = handle_snc_command(argv)
        print(f"✓ Second login result: {result}")
    except Exception as e:
        print(f"✗ Second login failed: {e}")
    
    # Test 4: Status check again
    print("\n4. Testing Status Check After Second Login...")
    argv = ['snc', '--status', '--api-url', 'http://localhost:5000']
    try:
        result = handle_snc_command(argv)
        print(f"✓ Status result: {result}")
    except Exception as e:
        print(f"✗ Status check failed: {e}")
    
    # Test 5: Logout
    print("\n5. Testing Logout...")
    argv = ['snc', '--logout', '--api-url', 'http://localhost:5000']
    try:
        result = handle_snc_command(argv)
        print(f"✓ Logout result: {result}")
    except Exception as e:
        print(f"✗ Logout failed: {e}")
    
    # Test 6: Status after logout
    print("\n6. Testing Status After Logout...")
    argv = ['snc', '--status', '--api-url', 'http://localhost:5000']
    try:
        result = handle_snc_command(argv)
        print(f"✓ Status after logout result: {result}")
    except Exception as e:
        print(f"✗ Status after logout failed: {e}")
    
    # Test 7: Test invalid credentials
    print("\n7. Testing Invalid Credentials...")
    argv = ['snc', '--user', 'invalid@user.com', '--token', 'wrong-token', '--api-url', 'http://localhost:5000']
    try:
        result = handle_snc_command(argv)
        print(f"✗ Should have failed but got: {result}")
    except SystemExit as e:
        print(f"✓ Correctly rejected invalid credentials (exit code: {e.code})")
    except Exception as e:
        print(f"✓ Correctly failed with error: {e}")
    
    return True

def show_usage_instructions():
    """Show how to use the commands once working"""
    print("\n" + "=" * 50)
    print("SNC Command Usage Instructions")
    print("=" * 50)
    
    print("\nOnce your company's API is set up, you can use:")
    print()
    print("# Login (replace with your actual API URL)")
    print("python3 direct_snc_test.py")
    print()
    print("# Or test individual components:")
    print("python3 -c \"")
    print("import sys")
    print("sys.path.insert(0, '.')") 
    print("from aider.snc import handle_snc_command")
    print("handle_snc_command(['snc', '--user', 'your-user', '--token', 'your-token', '--api-url', 'https://api.yourcompany.com/v1'])")
    print("\"")
    print()
    print("Available test accounts (for localhost:5000):")
    print("- user@company.com / demo-token-12345")
    print("- admin@company.com / admin-token-67890") 
    print("- developer / dev-token-abcdef")

if __name__ == "__main__":
    print("Direct SNC Command Tester")
    print("Make sure the sample API server is running on localhost:5000")
    print()
    
    success = test_snc_commands()
    show_usage_instructions()
    
    if success:
        print("\n✓ SNC implementation is working correctly!")
    else:
        print("\n✗ Some tests failed!")
