"""
SNC (Sync and Connect) module for web app integration with API support
"""

import os
import sys
import json
import requests
import time
import uuid
from pathlib import Path
from urllib.parse import urljoin


class SNCError(Exception):
    """Exception raised for SNC-related errors"""

    pass


class SnowCellModelProvider:
    """Provider for SnowCell deployed models"""

    # Mock available models for testing - replace with real API call
    AVAILABLE_MODELS = {
        "qwen": {
            "name": "Qwen/Qwen1.5-0.5B-Chat",
            "endpoint": "https://qwen-1-5b-chat-predictor.model-serving.snowcell.app/v1/chat/completions",
            "description": "Qwen 1.5 0.5B Chat Model",
        },
        "llama": {
            "name": "Meta-Llama/Llama-2-7b-chat",
            "endpoint": "https://llama-2-7b-chat-predictor.model-serving.snowcell.app/v1/chat/completions",
            "description": "Llama 2 7B Chat Model",
        },
        "mistral": {
            "name": "mistralai/Mistral-7B-Instruct",
            "endpoint": "https://mistral-7b-instruct-predictor.model-serving.snowcell.app/v1/chat/completions",
            "description": "Mistral 7B Instruct Model",
        },
    }

    @classmethod
    def get_available_models(cls):
        """Get list of available SnowCell models"""
        return cls.AVAILABLE_MODELS

    @classmethod
    def get_model_info(cls, model_key):
        """Get model information by key"""
        return cls.AVAILABLE_MODELS.get(model_key)

    @classmethod
    def list_models(cls):
        """List all available models"""
        print("\nAvailable SnowCell Models:")
        print("=" * 50)
        for key, info in cls.AVAILABLE_MODELS.items():
            print(f"Key: {key}")
            print(f"  Name: {info['name']}")
            print(f"  Description: {info['description']}")
            print(f"  Endpoint: {info['endpoint']}")
            print()

    @classmethod
    def make_chat_request(
        cls, model_key, messages, temperature=0.7, max_tokens=300, mock_mode=True
    ):
        """Make a chat completion request to SnowCell model"""
        model_info = cls.get_model_info(model_key)
        if not model_info:
            raise SNCError(f"Model '{model_key}' not found in available models")

        if mock_mode:
            # Return mock response for testing
            return {
                "id": "chatcmpl-mock-123",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_info["name"],
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": f"Hello! This is a mock response from {model_info['name']} ({model_key}). The model is working correctly!",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30,
                },
            }

        payload = {
            "model": model_info["name"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(
                model_info["endpoint"],
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise SNCError(f"Failed to make request to SnowCell model: {e}")


class SNCAPIClient:
    """API client for SNC operations"""

    # Shared mock data across all instances for testing
    _mock_sessions = {}
    _mock_users = {
        "user@company.com": {
            "name": "John Doe",
            "email": "user@company.com",
            "organization": "Your Company",
            "token": "demo-token-12345",
        },
        "admin@company.com": {
            "name": "Jane Admin",
            "email": "admin@company.com",
            "organization": "Your Company",
            "token": "admin-token-67890",
        },
        "developer": {
            "name": "Dev User",
            "email": "dev@company.com",
            "organization": "Your Company",
            "token": "dev-token-abcdef",
        },
    }

    def __init__(self, base_url=None, timeout=30):
        # For testing purposes - using mock responses instead of real API calls
        self.base_url = base_url or "https://api.example.com/v1"
        self.timeout = timeout

    def login(self, user_input, token):
        """
        Authenticate with the API (Mock implementation for testing)

        Args:
            user_input (str): User identification (username, email, etc.)
            token (str): Authentication token

        Returns:
            dict: API response containing user info and session data
        """
        try:
            # Mock authentication logic
            if (
                user_input in self._mock_users
                and self._mock_users[user_input]["token"] == token
            ):
                # Generate mock session token
                session_token = str(uuid.uuid4())

                # Store mock session
                self._mock_sessions[session_token] = {
                    "user": user_input,
                    "created_at": time.time(),
                    "last_activity": time.time(),
                }

                # Return mock successful response
                return {
                    "success": True,
                    "message": "Login successful",
                    "session_token": session_token,
                    "user_info": {
                        **self._mock_users[user_input],
                        "login_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                }
            else:
                # Return mock failed response
                raise SNCError("Invalid credentials")

        except SNCError:
            raise
        except Exception as e:
            raise SNCError(f"Login failed: {str(e)}")

    def logout(self, session_token):
        """
        Logout from the API (Mock implementation for testing)

        Args:
            session_token (str): Session token to invalidate

        Returns:
            dict: API response
        """
        try:
            # Mock logout logic
            if session_token and session_token in self._mock_sessions:
                user = self._mock_sessions[session_token]["user"]
                del self._mock_sessions[session_token]
                return {
                    "success": True,
                    "message": f"Logged out successfully for user: {user}",
                }
            else:
                return {
                    "success": True,
                    "message": "Logged out (no active session found)",
                }

        except Exception as e:
            # For logout, we proceed even if there are errors
            return {"success": True, "message": "Logged out locally"}

    def status(self, session_token):
        """
        Check session status with the API (Mock implementation for testing)

        Args:
            session_token (str): Session token to validate

        Returns:
            dict: API response with session status
        """
        try:
            # Mock status check logic
            if not session_token:
                return {"success": False, "message": "No session token provided"}

            if session_token in self._mock_sessions:
                session = self._mock_sessions[session_token]
                user_input = session["user"]

                # Update last activity
                session["last_activity"] = time.time()

                return {
                    "success": True,
                    "message": "Session is active",
                    "user_info": {
                        **self._mock_users[user_input],
                        "last_activity": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "session_duration": f"{int(time.time() - session['created_at'])} seconds",
                    },
                    "expires_at": "Never (mock session)",
                }
            else:
                return {"success": False, "message": "Session expired or invalid"}

        except Exception as e:
            raise SNCError(f"Status check failed: {str(e)}")


class SNCAider:
    """Handle SNC (Sync and Connect) operations for web app integration"""

    def __init__(self, io=None, api_base_url=None):
        self.io = io
        self.config_file = Path.home() / ".aider" / "snc_config.json"
        self.api_client = SNCAPIClient(base_url=api_base_url)

    def _log(self, message):
        """Log message to io or print"""
        if self.io:
            self.io.tool_output(message)
        else:
            print(message)

    def _error(self, message):
        """Log error message"""
        if self.io:
            self.io.tool_error(message)
        else:
            print(f"Error: {message}", file=sys.stderr)

    def login(self, user_input, token):
        """
        Login to the web app with user input and token

        Args:
            user_input (str): User identification input (username, email, etc.)
            token (str): Authentication token
        """
        if not user_input or not user_input.strip():
            raise SNCError("User input cannot be empty")

        if not token or not token.strip():
            raise SNCError("Token cannot be empty")

        self._log("Authenticating with API...")

        try:
            # Call API for authentication
            api_response = self.api_client.login(user_input.strip(), token.strip())

            # Create config directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Store login credentials and API response
            config_data = {
                "user_input": user_input.strip(),
                "token": token.strip(),
                "status": "logged_in",
                "session_token": api_response.get("session_token", ""),
                "user_info": api_response.get("user_info", {}),
                "login_time": int(time.time()),
                "api_response": api_response,
            }

            with open(self.config_file, "w") as f:
                json.dump(config_data, f, indent=2)

            self._log(f"✓ Successfully logged in as: {user_input}")
            if api_response.get("user_info"):
                user_info = api_response["user_info"]
                if user_info.get("name"):
                    self._log(f"  Name: {user_info['name']}")
                if user_info.get("email"):
                    self._log(f"  Email: {user_info['email']}")
                if user_info.get("organization"):
                    self._log(f"  Organization: {user_info['organization']}")

            self._log(f"  Config saved to: {self.config_file}")

        except SNCError:
            raise
        except Exception as e:
            raise SNCError(f"Failed to save login config: {e}")

    def select_model(self, model_key):
        """
        Select a SnowCell model for chat operations

        Args:
            model_key (str): Key of the model to select (e.g., 'qwen', 'llama', 'mistral')
        """
        # Check if user is logged in
        if not self.config_file.exists():
            raise SNCError(
                "Not logged in. Please login first with: aider snc --user <user> --token <token>"
            )

        # Validate model exists
        model_info = SnowCellModelProvider.get_model_info(model_key)
        if not model_info:
            available_models = list(SnowCellModelProvider.get_available_models().keys())
            raise SNCError(
                f"Model '{model_key}' not found. Available models: {', '.join(available_models)}"
            )

        try:
            # Read current config
            with open(self.config_file, "r") as f:
                config = json.load(f)

            # Add selected model to config
            config["selected_model"] = {
                "key": model_key,
                "name": model_info["name"],
                "endpoint": model_info["endpoint"],
                "description": model_info["description"],
                "selected_at": int(time.time()),
            }

            # Save updated config
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)

            self._log(f"✓ Selected SnowCell model: {model_key}")
            self._log(f"  Name: {model_info['name']}")
            self._log(f"  Description: {model_info['description']}")
            self._log(f"  Endpoint: {model_info['endpoint']}")
            self._log(f"  Config updated: {self.config_file}")

            # Show usage instructions
            self._log(f"\nTo start chatting with this model, use:")
            self._log(f"  python -m aider --model snowcell:{model_key}")

        except Exception as e:
            raise SNCError(f"Failed to select model: {e}")

    def list_models(self):
        """List available SnowCell models"""
        self._log("Available SnowCell Models:")
        self._log("=" * 50)

        models = SnowCellModelProvider.get_available_models()
        for key, info in models.items():
            self._log(f"Key: {key}")
            self._log(f"  Name: {info['name']}")
            self._log(f"  Description: {info['description']}")
            self._log(f"  Endpoint: {info['endpoint'][:60]}...")
            self._log("")

        self._log("Usage:")
        self._log("  aider snc <model_key>  # Select a model")
        self._log("  aider --model snowcell:<model_key>  # Use selected model for chat")

    def get_selected_model(self):
        """Get currently selected model info"""
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            return config.get("selected_model")
        except Exception:
            return None

    def test_model(self, model_key=None, mock_mode=True):
        """Test the selected or specified model with a simple request"""
        if model_key:
            model_info = SnowCellModelProvider.get_model_info(model_key)
            if not model_info:
                raise SNCError(f"Model '{model_key}' not found")
        else:
            selected_model = self.get_selected_model()
            if not selected_model:
                raise SNCError(
                    "No model selected. Use 'aider snc <model_key>' to select a model first."
                )
            model_key = selected_model["key"]

        self._log(
            f"Testing SnowCell model: {model_key} ({'mock mode' if mock_mode else 'real API'})"
        )

        test_messages = [
            {"role": "user", "content": "Hello! Please respond with a brief greeting."}
        ]

        try:
            response = SnowCellModelProvider.make_chat_request(
                model_key,
                test_messages,
                temperature=0.7,
                max_tokens=100,
                mock_mode=mock_mode,
            )

            self._log("✓ Model test successful!")
            if response.get("choices") and len(response["choices"]) > 0:
                message = response["choices"][0].get("message", {})
                content = message.get("content", "No content")
                self._log(f"Response: {content}")
            else:
                self._log(f"Raw response: {response}")

        except Exception as e:
            self._log(f"✗ Model test failed: {e}")
            if not mock_mode:
                self._log("Try with mock mode: aider snc --test-model")
            raise SNCError(f"Model test failed: {e}")

    def logout(self):
        """Logout and clear stored credentials"""
        try:
            if self.config_file.exists():
                # Read current config to get session token
                with open(self.config_file, "r") as f:
                    config = json.load(f)

                session_token = config.get("session_token")

                # Call API to invalidate session
                if session_token:
                    self._log("Logging out from API...")
                    try:
                        self.api_client.logout(session_token)
                        self._log("✓ Successfully logged out from API")
                    except Exception as e:
                        self._log(
                            f"Warning: API logout failed ({e}), proceeding with local logout"
                        )

                # Remove local config file
                self.config_file.unlink()
                self._log("✓ Local session cleared")
            else:
                self._log("No active session found")

        except Exception as e:
            raise SNCError(f"Failed to logout: {e}")

    def status(self):
        """Check current login status"""
        try:
            if not self.config_file.exists():
                self._log("Status: Not logged in")
                return

            with open(self.config_file, "r") as f:
                config = json.load(f)

            user_input = config.get("user_input", "Unknown")
            local_status = config.get("status", "Unknown")
            session_token = config.get("session_token")
            login_time = config.get("login_time", 0)

            self._log(f"Local Status: {local_status}")
            self._log(f"User: {user_input}")

            if login_time:
                login_datetime = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(login_time)
                )
                self._log(f"Login Time: {login_datetime}")

            # Check status with API
            if session_token:
                self._log("Checking session with API...")
                try:
                    api_response = self.api_client.status(session_token)
                    if api_response.get("success"):
                        self._log("✓ API Session: Active")
                        if api_response.get("user_info"):
                            user_info = api_response["user_info"]
                            if user_info.get("last_activity"):
                                self._log(
                                    f"  Last Activity: {user_info['last_activity']}"
                                )
                        if api_response.get("expires_at"):
                            self._log(
                                f"  Session Expires: {api_response['expires_at']}"
                            )
                    else:
                        self._log("⚠ API Session: Expired or Invalid")
                        self._log("  Consider logging in again")

                except SNCError as e:
                    self._log(f"⚠ API Status Check Failed: {e}")
                except Exception as e:
                    self._log(f"⚠ Unexpected error checking API status: {e}")
            else:
                self._log("⚠ No session token found")

        except Exception as e:
            raise SNCError(f"Failed to check status: {e}")

    def get_config(self):
        """Get current configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    return json.load(f)
            return None
        except Exception as e:
            raise SNCError(f"Failed to read config: {e}")


def handle_snc_command(argv):
    """
    Handle SNC subcommand

    Args:
        argv (list): Command line arguments

    Returns:
        bool: True if SNC command was handled, False otherwise
    """
    if not argv or argv[0] != "snc":
        return False

    import argparse

    parser = argparse.ArgumentParser(
        prog="aider snc",
        description="SNC (Sync and Connect) operations for web app integration",
    )

    # Positional argument for model selection
    parser.add_argument(
        "model", nargs="?", help="Select SnowCell model (e.g., qwen, llama, mistral)"
    )

    # Create mutually exclusive group for different actions
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--logout", action="store_true", help="Logout from web app")
    group.add_argument("--status", action="store_true", help="Check login status")
    group.add_argument(
        "--list-models", action="store_true", help="List available SnowCell models"
    )
    group.add_argument(
        "--test-model", action="store_true", help="Test the selected model"
    )

    # Login arguments (required when not using logout or status)
    parser.add_argument("--user", help="User input (username, email, etc.)")
    parser.add_argument("--token", help="Authentication token")

    # Optional API configuration
    parser.add_argument("--api-url", help="Custom API base URL")
    parser.add_argument(
        "--timeout", type=int, default=30, help="API request timeout in seconds"
    )

    try:
        args = parser.parse_args(argv[1:])
        snc = SNCAider(api_base_url=args.api_url)

        # Set timeout if provided
        if hasattr(args, "timeout"):
            snc.api_client.timeout = args.timeout

        if args.logout:
            snc.logout()
        elif args.status:
            snc.status()
        elif args.list_models:
            snc.list_models()
        elif args.test_model:
            snc.test_model()
        elif args.model:
            # Model selection
            snc.select_model(args.model)
        else:
            # Default action is login when user and token are provided
            if not args.user or not args.token:
                parser.error(
                    "--user and --token are required for login, or specify a model to select"
                )
            snc.login(args.user, args.token)

    except SNCError as e:
        print(f"SNC Error: {e}", file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        # Let argparse handle its own exits
        raise
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    return True


# Sample API server implementation for testing
def create_sample_api():
    """
    Create a sample API server for testing purposes
    This is just for demonstration - replace with your actual API
    """
    sample_api_code = """
from flask import Flask, request, jsonify
import time
import uuid

app = Flask(__name__)

# Simple in-memory storage for demo
sessions = {}
users = {
    "user@company.com": {
        "name": "John Doe",
        "email": "user@company.com",
        "organization": "Your Company",
        "token": "demo-token-12345"
    }
}

@app.route('/v1/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user_input = data.get('user_input')
    token = data.get('token')
    
    # Simple validation
    if user_input in users and users[user_input]['token'] == token:
        session_token = str(uuid.uuid4())
        sessions[session_token] = {
            'user': user_input,
            'created_at': time.time()
        }
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'session_token': session_token,
            'user_info': users[user_input]
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid credentials'
        }), 401

@app.route('/v1/auth/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]
        if token in sessions:
            del sessions[token]
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@app.route('/v1/auth/status', methods=['GET'])
def status():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({
            'success': False,
            'message': 'No authorization header'
        }), 401
    
    token = auth_header[7:]
    if token not in sessions:
        return jsonify({
            'success': False,
            'message': 'Invalid session'
        }), 401
    
    session = sessions[token]
    user_input = session['user']
    
    return jsonify({
        'success': True,
        'message': 'Session active',
        'user_info': {
            **users[user_input],
            'last_activity': time.strftime('%Y-%m-%d %H:%M:%S'),
            'session_duration': int(time.time() - session['created_at'])
        },
        'expires_at': 'Never (demo)'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
"""

    return sample_api_code
