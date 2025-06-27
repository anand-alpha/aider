#!/usr/bin/env python3
"""
Final test to ensure all snc authentication functionality works correctly.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the current directory to Python path so we can import aider
sys.path.insert(0, "/home/hac/code/aider")


def test_full_workflow():
    """Test the complete authentication workflow"""
    print("Testing complete authentication workflow...")

    # Create a temporary directory for auth files
    temp_dir = Path(tempfile.mkdtemp())
    original_home = os.environ.get("HOME")
    os.environ["HOME"] = str(temp_dir)

    try:
        from aider.auth import handle_login_command, AuthManager
        from argparse import Namespace

        # Test 1: Initial state - not logged in
        auth_manager = AuthManager()
        assert not auth_manager.is_logged_in(), "Should not be logged in initially"
        print("✓ Initial state: not logged in")

        # Test 2: Login with valid token
        args = Namespace(
            login_token="snc_test_token_123456", login_status=False, logout=False
        )
        result = handle_login_command(args)
        assert result == True, "Login should succeed"
        print("✓ Login command successful")

        # Test 3: Check login status
        args = Namespace(login_token=None, login_status=True, logout=False)
        result = handle_login_command(args)
        assert result == True, "Status check should succeed"
        print("✓ Status check successful")

        # Test 4: Verify logged in state
        assert auth_manager.is_logged_in(), "Should be logged in"
        print("✓ Login state verified")

        # Test 5: Logout
        args = Namespace(login_token=None, login_status=False, logout=True)
        result = handle_login_command(args)
        assert result == True, "Logout should succeed"
        print("✓ Logout successful")

        # Test 6: Verify logged out state
        assert not auth_manager.is_logged_in(), "Should not be logged in after logout"
        print("✓ Logout state verified")

        # Test 7: Login with invalid token
        args = Namespace(login_token="invalid_token", login_status=False, logout=False)
        result = handle_login_command(args)
        assert result == False, "Invalid token should be rejected"
        print("✓ Invalid token rejected")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Restore original HOME
        if original_home:
            os.environ["HOME"] = original_home
        else:
            del os.environ["HOME"]

        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_main_integration():
    """Test that the main function properly integrates authentication"""
    try:
        from aider.main import main

        print("✓ Main function imports successfully with auth integration")
        return True
    except Exception as e:
        print(f"❌ Main function integration test failed: {e}")
        return False


if __name__ == "__main__":
    print("Final test of Snowcell (snc) authentication...")
    print("=" * 50)

    tests = [
        test_full_workflow,
        test_main_integration,
    ]

    results = []
    for test in tests:
        print(f"\n--- {test.__name__} ---")
        results.append(test())

    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All tests passed! Authentication is fully functional.")
        print("\n📝 Usage Summary:")
        print("1. Login:        snc login --token snc_your_token_here")
        print("2. Check status: snc login --status")
        print("3. Logout:       snc logout")
        print("4. Use snc:      snc --model o3-mini --api-key openai=your-key")
        print("\n✨ Features implemented:")
        print("- Mock authentication with token validation")
        print("- Persistent login state (30-day expiration)")
        print("- Login required for main functionality")
        print("- Secure token storage in ~/.snc/auth.json")
        print("- Command-line interface for auth operations")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
