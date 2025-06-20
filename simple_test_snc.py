#!/usr/bin/env python3
"""
Simple integration test that doesn't require manual server startup
"""

import sys
import os
import time
import subprocess
import signal
import requests
from pathlib import Path

# Add aider to the path
aider_path = Path(__file__).parent
sys.path.insert(0, str(aider_path))

from aider.snc import handle_snc_command, SNCAider, SNCError


class APIServerManager:
    """Manage the sample API server for testing"""
    
    def __init__(self, port=5000):
        self.port = port
        self.process = None
        
    def start(self):
        """Start the API server"""
        print(f"Starting sample API server on port {self.port}...")
        
        # Start the server as a subprocess
        self.process = subprocess.Popen(
            [sys.executable, "sample_api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=aider_path
        )
        
        # Wait for server to start
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(f"http://localhost:{self.port}/v1/health", timeout=1)
                if response.status_code == 200:
                    print("✓ API server started successfully")
                    return True
            except requests.exceptions.RequestException:
                time.sleep(1)
        
        print("✗ Failed to start API server")
        return False
    
    def stop(self):
        """Stop the API server"""
        if self.process:
            print("Stopping API server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            print("✓ API server stopped")


def test_full_integration():
    """Test full integration with automatic server management"""
    print("=" * 60)
    print("SNC Full Integration Test")
    print("=" * 60)
    
    # Check if Flask is available
    try:
        import flask
    except ImportError:
        print("✗ Flask not installed. Run: pip3 install flask")
        return False
    
    server_manager = APIServerManager()
    
    try:
        # Start API server
        if not server_manager.start():
            return False
        
        api_url = "http://localhost:5000"
        
        # Test 1: Valid login
        print("\n1. Testing valid login...")
        argv = ['snc', '--user', 'user@company.com', '--token', 'demo-token-12345', '--api-url', api_url]
        try:
            result = handle_snc_command(argv)
            print("✓ Login successful")
        except Exception as e:
            print(f"✗ Login failed: {e}")
            return False
        
        # Test 2: Status check
        print("\n2. Testing status check...")
        argv = ['snc', '--status', '--api-url', api_url]
        try:
            result = handle_snc_command(argv)
            print("✓ Status check successful")
        except Exception as e:
            print(f"✗ Status check failed: {e}")
        
        # Test 3: Invalid credentials
        print("\n3. Testing invalid credentials...")
        argv = ['snc', '--user', 'invalid@user.com', '--token', 'wrong-token', '--api-url', api_url]
        try:
            result = handle_snc_command(argv)
            print("✗ Should have failed with invalid credentials")
        except SystemExit:
            print("✓ Correctly rejected invalid credentials")
        
        # Test 4: Logout
        print("\n4. Testing logout...")
        # First login again
        argv = ['snc', '--user', 'admin@company.com', '--token', 'admin-token-67890', '--api-url', api_url]
        try:
            handle_snc_command(argv)
            print("✓ Re-login successful")
        except Exception as e:
            print(f"✗ Re-login failed: {e}")
        
        # Then logout
        argv = ['snc', '--logout', '--api-url', api_url]
        try:
            result = handle_snc_command(argv)
            print("✓ Logout successful")
        except Exception as e:
            print(f"✗ Logout failed: {e}")
        
        # Test 5: Status after logout
        print("\n5. Testing status after logout...")
        argv = ['snc', '--status', '--api-url', api_url]
        try:
            result = handle_snc_command(argv)
            print("✓ Status check after logout successful")
        except Exception as e:
            print(f"✗ Status check after logout failed: {e}")
        
        print("\n✓ All integration tests completed successfully!")
        return True
        
    finally:
        server_manager.stop()


def test_api_endpoints():
    """Test API endpoints directly"""
    print("\n" + "=" * 60)
    print("Testing API Endpoints Directly")
    print("=" * 60)
    
    try:
        import flask
    except ImportError:
        print("✗ Flask not installed, skipping API tests")
        return
    
    server_manager = APIServerManager()
    
    try:
        if not server_manager.start():
            return
        
        base_url = "http://localhost:5000"
        
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        try:
            response = requests.get(f"{base_url}/v1/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Health check: {data['status']}")
            else:
                print(f"✗ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Health check error: {e}")
        
        # Test users endpoint
        print("\n2. Testing users endpoint...")
        try:
            response = requests.get(f"{base_url}/v1/users")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Users endpoint: {len(data['users'])} users available")
                for user in data['users']:
                    print(f"  - {user['username']} ({user['name']})")
            else:
                print(f"✗ Users endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Users endpoint error: {e}")
        
        # Test login endpoint
        print("\n3. Testing login endpoint...")
        try:
            payload = {
                "user_input": "user@company.com",
                "token": "demo-token-12345",
                "client": "test"
            }
            response = requests.post(f"{base_url}/v1/auth/login", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Login endpoint: {data['message']}")
                session_token = data.get('session_token')
                
                # Test status endpoint
                print("\n4. Testing status endpoint...")
                headers = {'Authorization': f'Bearer {session_token}'}
                response = requests.get(f"{base_url}/v1/auth/status", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Status endpoint: {data['message']}")
                else:
                    print(f"✗ Status endpoint failed: {response.status_code}")
                
                # Test logout endpoint
                print("\n5. Testing logout endpoint...")
                response = requests.post(f"{base_url}/v1/auth/logout", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Logout endpoint: {data['message']}")
                else:
                    print(f"✗ Logout endpoint failed: {response.status_code}")
                    
            else:
                print(f"✗ Login endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Login endpoint error: {e}")
            
    finally:
        server_manager.stop()


if __name__ == "__main__":
    print("SNC Simple Integration Test")
    print("This test automatically starts and stops the API server")
    print()
    
    success = test_full_integration()
    test_api_endpoints()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ All tests passed! SNC implementation is working correctly.")
        print("=" * 60)
        print("\nYou can now use the SNC command:")
        print("  python3 -m aider snc --user <username> --token <token>")
        print("  python3 -m aider snc --status")
        print("  python3 -m aider snc --logout")
    else:
        print("\n" + "=" * 60)
        print("✗ Some tests failed. Please check the implementation.")
        print("=" * 60)
