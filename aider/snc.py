"""
SNC (Sync and Connect) module for web app integration with API support
"""
import os
import sys
import json
import requests
import time
from pathlib import Path
from urllib.parse import urljoin


class SNCError(Exception):
    """Exception raised for SNC-related errors"""
    pass


class SNCAPIClient:
    """API client for SNC operations"""
    
    def __init__(self, base_url=None, timeout=30):
        # Default to a sample API endpoint - replace with your company's API
        self.base_url = base_url or "https://api.example.com/v1"
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Aider-SNC/1.0'
        })
    
    def login(self, user_input, token):
        """
        Authenticate with the API
        
        Args:
            user_input (str): User identification (username, email, etc.)
            token (str): Authentication token
            
        Returns:
            dict: API response containing user info and session data
        """
        endpoint = urljoin(self.base_url, "v1/auth/login")
        
        payload = {
            "user_input": user_input,
            "token": token,
            "client": "aider",
            "timestamp": int(time.time())
        }
        
        try:
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('success', False):
                raise SNCError(f"Login failed: {data.get('message', 'Unknown error')}")
            
            return data
            
        except requests.exceptions.Timeout:
            raise SNCError("API request timed out")
        except requests.exceptions.ConnectionError:
            raise SNCError("Failed to connect to API server")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise SNCError("Invalid credentials")
            elif e.response.status_code == 403:
                raise SNCError("Access denied")
            else:
                raise SNCError(f"API error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise SNCError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            raise SNCError("Invalid response from API")
    
    def logout(self, session_token):
        """
        Logout from the API
        
        Args:
            session_token (str): Session token to invalidate
            
        Returns:
            dict: API response
        """
        endpoint = urljoin(self.base_url, "v1/auth/logout")
        
        headers = {
            'Authorization': f'Bearer {session_token}'
        }
        
        try:
            response = self.session.post(
                endpoint,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # For logout, we might want to proceed even if API call fails
            return {"success": True, "message": "Logged out locally"}
    
    def status(self, session_token):
        """
        Check session status with the API
        
        Args:
            session_token (str): Session token to validate
            
        Returns:
            dict: API response with session status
        """
        endpoint = urljoin(self.base_url, "v1/auth/status")
        
        headers = {
            'Authorization': f'Bearer {session_token}'
        }
        
        try:
            response = self.session.get(
                endpoint,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return {"success": False, "message": "Session expired"}
            else:
                raise SNCError(f"Status check failed: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
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
                "api_response": api_response
            }
            
            with open(self.config_file, 'w') as f:
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
    
    def logout(self):
        """Logout and clear stored credentials"""
        try:
            if self.config_file.exists():
                # Read current config to get session token
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                session_token = config.get('session_token')
                
                # Call API to invalidate session
                if session_token:
                    self._log("Logging out from API...")
                    try:
                        self.api_client.logout(session_token)
                        self._log("✓ Successfully logged out from API")
                    except Exception as e:
                        self._log(f"Warning: API logout failed ({e}), proceeding with local logout")
                
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
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            user_input = config.get('user_input', 'Unknown')
            local_status = config.get('status', 'Unknown')
            session_token = config.get('session_token')
            login_time = config.get('login_time', 0)
            
            self._log(f"Local Status: {local_status}")
            self._log(f"User: {user_input}")
            
            if login_time:
                login_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(login_time))
                self._log(f"Login Time: {login_datetime}")
            
            # Check status with API
            if session_token:
                self._log("Checking session with API...")
                try:
                    api_response = self.api_client.status(session_token)
                    if api_response.get('success'):
                        self._log("✓ API Session: Active")
                        if api_response.get('user_info'):
                            user_info = api_response['user_info']
                            if user_info.get('last_activity'):
                                self._log(f"  Last Activity: {user_info['last_activity']}")
                        if api_response.get('expires_at'):
                            self._log(f"  Session Expires: {api_response['expires_at']}")
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
                with open(self.config_file, 'r') as f:
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
    if not argv or argv[0] != 'snc':
        return False
    
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='aider snc',
        description='SNC (Sync and Connect) operations for web app integration'
    )
    
    # Create mutually exclusive group for different actions
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--logout', action='store_true', help='Logout from web app')
    group.add_argument('--status', action='store_true', help='Check login status')
    
    # Login arguments (required when not using logout or status)
    parser.add_argument('--user', help='User input (username, email, etc.)')
    parser.add_argument('--token', help='Authentication token')
    
    # Optional API configuration
    parser.add_argument('--api-url', help='Custom API base URL')
    parser.add_argument('--timeout', type=int, default=30, help='API request timeout in seconds')
    
    try:
        args = parser.parse_args(argv[1:])
        snc = SNCAider(api_base_url=args.api_url)
        
        # Set timeout if provided
        if hasattr(args, 'timeout'):
            snc.api_client.timeout = args.timeout
        
        if args.logout:
            snc.logout()
        elif args.status:
            snc.status()
        else:
            # Default action is login when user and token are provided
            if not args.user or not args.token:
                parser.error("--user and --token are required for login")
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
    sample_api_code = '''
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
'''
    
    return sample_api_code
