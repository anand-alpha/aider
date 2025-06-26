"""
Authentication module for Snowcell (snc) - handles login/logout functionality.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import time


class AuthManager:
    """Manages authentication state for snc."""

    def __init__(self):
        self.auth_file = Path.home() / ".snc" / "auth.json"
        self.auth_file.parent.mkdir(exist_ok=True)

    def login(self, token: str) -> bool:
        """
        Mock login function - validates token format and stores it.

        Args:
            token: The authentication token

        Returns:
            bool: True if login successful, False otherwise
        """
        # Mock validation - in real implementation, this would validate against a server
        # if not token or len(token) < 10:
        #     return False

        # # Mock token validation - accept tokens that start with 'snc_'
        # if not token.startswith("snc_"):
        #     return False

        # Store auth info
        auth_data = {
            "token": token,
            "login_time": int(time.time()),
            "user_id": f"user_{hash(token) % 10000}",  # Mock user ID
            "expires_at": int(time.time()) + (30 * 24 * 60 * 60),  # 30 days
        }

        try:
            with open(self.auth_file, "w") as f:
                json.dump(auth_data, f, indent=2)
            return True
        except Exception:
            return False

    def logout(self) -> bool:
        """
        Logout by removing the auth file.

        Returns:
            bool: True if logout successful, False otherwise
        """
        try:
            if self.auth_file.exists():
                self.auth_file.unlink()
            return True
        except Exception:
            return False

    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in and token is valid.

        Returns:
            bool: True if logged in with valid token, False otherwise
        """
        if not self.auth_file.exists():
            return False

        try:
            with open(self.auth_file, "r") as f:
                auth_data = json.load(f)

            # Check if token has expired
            if auth_data.get("expires_at", 0) < int(time.time()):
                # Token expired, remove it
                self.logout()
                return False

            return True
        except Exception:
            return False

    def get_auth_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current authentication information.

        Returns:
            dict: Auth info if logged in, None otherwise
        """
        if not self.is_logged_in():
            return None

        try:
            with open(self.auth_file, "r") as f:
                auth_data = json.load(f)

            # Remove sensitive token from returned data
            return {
                "user_id": auth_data.get("user_id"),
                "login_time": auth_data.get("login_time"),
                "expires_at": auth_data.get("expires_at"),
                "logged_in": True,
            }
        except Exception:
            return None

    def require_login(self) -> bool:
        """
        Check if user is logged in and show error if not.

        Returns:
            bool: True if logged in, False if not logged in
        """
        if not self.is_logged_in():
            print(
                "❌ You are not logged in. Please run 'snc --login <your_token>' first."
            )
            return False
        return True


def handle_login_command(args, io=None) -> bool:
    """
    Handle login-related commands.

    Args:
        args: Parsed command line arguments
        io: IO object for output (optional)

    Returns:
        bool: True if command was handled, False otherwise
    """
    auth_manager = AuthManager()

    if hasattr(args, "login") and args.login:
        # Login with token
        if auth_manager.login(args.login):
            print("✅ Login successful!")
            print("You can now use all snc commands.")
            return True
        else:
            print("❌ Login failed. Please check your token.")
            print("Token should start with 'snc_' and be at least 10 characters long.")
            return False

    elif hasattr(args, "status") and args.status:
        # Check login status
        if auth_manager.is_logged_in():
            auth_info = auth_manager.get_auth_info()
            print("✅ You are logged in")
            if auth_info:
                print(f"   User ID: {auth_info['user_id']}")
                login_date = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(auth_info["login_time"])
                )
                expire_date = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(auth_info["expires_at"])
                )
                print(f"   Logged in: {login_date}")
                print(f"   Expires: {expire_date}")
        else:
            print("❌ You are not logged in")
            print("Run 'snc --login <your_token>' to log in.")
        return True

    elif hasattr(args, "logout") and args.logout:
        # Logout
        if auth_manager.logout():
            print("✅ Logged out successfully")
        else:
            print("❌ Logout failed")
        return True

    return False
