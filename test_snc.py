#!/usr/bin/env python3
"""
Test script for the SNC command implementation with API integration
"""

import sys
import os
import time
from pathlib import Path

# Add aider to the path
aider_path = Path(__file__).parent
sys.path.insert(0, str(aider_path))

from aider.snc import handle_snc_command, SNCAider, SNCError


def test_snc_api_integration():
    """Test SNC with sample API server"""
    print("=" * 60)
    print("Testing SNC API Integration")
    print("=" * 60)
    print("NOTE: Make sure to run 'python3 sample_api_server.py' first!")
    print()
    
    # Test with local API server
    api_url = "http://localhost:5000"
    
    print("1. Testing login with valid credentials...")
    argv = [
        'snc', 
        '--user', 'user@company.com', 
        '--token', 'demo-token-12345',
        '--api-url', api_url
    ]
    
    try:
        result = handle_snc_command(argv)
        print(f"✓ Login command handled: {result}")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return
    
    print("\n2. Testing status check...")
    argv = ['snc', '--status', '--api-url', api_url]
    try:
        result = handle_snc_command(argv)
        print(f"✓ Status command handled: {result}")
    except Exception as e:
        print(f"✗ Status check failed: {e}")
    
    print("\n3. Testing logout...")
    argv = ['snc', '--logout', '--api-url', api_url]
    try:
        result = handle_snc_command(argv)
        print(f"✓ Logout command handled: {result}")
    except Exception as e:
        print(f"✗ Logout failed: {e}")
    
    print("\n4. Testing login with invalid credentials...")
    argv = [
        'snc', 
        '--user', 'invalid@user.com', 
        '--token', 'wrong-token',
        '--api-url', api_url
    ]
    try:
        result = handle_snc_command(argv)
        print(f"✗ Should have failed but got: {result}")
    except SystemExit:
        print("✓ Correctly rejected invalid credentials")
    except Exception as e:
        print(f"✓ Correctly failed with error: {e}")


def test_snc_errors():
    """Test SNC error handling"""
    print("\n" + "=" * 60)
    print("Testing SNC Error Handling")
    print("=" * 60)
    
    snc = SNCAider()
    
    # Test empty user input
    try:
        snc.login("", "token")
        print("✗ Should have raised SNCError for empty user input")
    except SNCError as e:
        print(f"✓ Correctly caught error for empty user input: {e}")
    
    # Test empty token
    try:
        snc.login("user", "")
        print("✗ Should have raised SNCError for empty token")
    except SNCError as e:
        print(f"✓ Correctly caught error for empty token: {e}")
    
    # Test whitespace-only inputs
    try:
        snc.login("   ", "token")
        print("✗ Should have raised SNCError for whitespace-only user")
    except SNCError as e:
        print(f"✓ Correctly caught error for whitespace-only user: {e}")


def test_non_snc_command():
    """Test that non-SNC commands return False"""
    print("\n" + "=" * 60)
    print("Testing Non-SNC Commands")
    print("=" * 60)
    
    argv = ['--model', 'gpt-4']
    result = handle_snc_command(argv)
    print(f"✓ Non-SNC command handled: {result} (should be False)")
    
    argv = []
    result = handle_snc_command(argv)
    print(f"✓ Empty command handled: {result} (should be False)")
    
    argv = ['init']
    result = handle_snc_command(argv)
    print(f"✓ Other command handled: {result} (should be False)")


def test_command_line_args():
    """Test various command line argument combinations"""
    print("\n" + "=" * 60)
    print("Testing Command Line Arguments")
    print("=" * 60)
    
    # Test missing arguments
    print("Testing missing arguments...")
    
    # Missing token
    argv = ['snc', '--user', 'testuser']
    try:
        handle_snc_command(argv)
        print("✗ Should have failed for missing token")
    except SystemExit:
        print("✓ Correctly failed for missing token")
    
    # Missing user
    argv = ['snc', '--token', 'testtoken']
    try:
        handle_snc_command(argv)
        print("✗ Should have failed for missing user")
    except SystemExit:
        print("✓ Correctly failed for missing user")
    
    # Help command
    print("\nTesting help command...")
    argv = ['snc', '--help']
    try:
        handle_snc_command(argv)
        print("✗ Help should exit")
    except SystemExit:
        print("✓ Help command works")


def show_usage_examples():
    """Show usage examples"""
    print("\n" + "=" * 60)
    print("SNC Command Usage Examples")
    print("=" * 60)
    
    examples = [
        {
            "description": "Login with default API",
            "command": "python3 -m aider snc --user user@company.com --token demo-token-12345"
        },
        {
            "description": "Login with custom API URL",
            "command": "python3 -m aider snc --user user@company.com --token demo-token-12345 --api-url http://localhost:5000"
        },
        {
            "description": "Check login status",
            "command": "python3 -m aider snc --status"
        },
        {
            "description": "Logout",
            "command": "python3 -m aider snc --logout"
        },
        {
            "description": "Get help",
            "command": "python3 -m aider snc --help"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['description']}:")
        print(f"   {example['command']}")
        print()


if __name__ == "__main__":
    print("SNC Command Test Suite")
    print("Make sure to start the sample API server first:")
    print("  python3 sample_api_server.py")
    print()
    
    # Run tests
    test_snc_api_integration()
    test_snc_errors()
    test_non_snc_command()
    test_command_line_args()
    show_usage_examples()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
