"""
Sample API server for testing SNC functionality
Run this server before testing the SNC commands
"""

from flask import Flask, request, jsonify
import time
import uuid
import json

app = Flask(__name__)

# Simple in-memory storage for demo
sessions = {}
users = {
    "user@company.com": {
        "name": "John Doe",
        "email": "user@company.com",
        "organization": "Your Company",
        "token": "demo-token-12345"
    },
    "admin@company.com": {
        "name": "Jane Admin",
        "email": "admin@company.com", 
        "organization": "Your Company",
        "token": "admin-token-67890"
    },
    "developer": {
        "name": "Dev User",
        "email": "dev@company.com",
        "organization": "Your Company", 
        "token": "dev-token-abcdef"
    }
}

@app.route('/v1/auth/login', methods=['POST'])
def login():
    """Handle login requests"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Invalid JSON payload'
            }), 400
            
        user_input = data.get('user_input', '').strip()
        token = data.get('token', '').strip()
        
        print(f"Login attempt: user={user_input}, token={token[:10]}...")
        
        # Simple validation
        if user_input in users and users[user_input]['token'] == token:
            session_token = str(uuid.uuid4())
            sessions[session_token] = {
                'user': user_input,
                'created_at': time.time(),
                'last_activity': time.time()
            }
            
            response_data = {
                'success': True,
                'message': 'Login successful',
                'session_token': session_token,
                'user_info': {
                    **users[user_input],
                    'login_time': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            print(f"Login successful for {user_input}")
            return jsonify(response_data)
        else:
            print(f"Login failed for {user_input} - invalid credentials")
            return jsonify({
                'success': False,
                'message': 'Invalid username or token'
            }), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/v1/auth/logout', methods=['POST'])
def logout():
    """Handle logout requests"""
    try:
        auth_header = request.headers.get('Authorization', '')
        print(f"Logout request with auth: {auth_header[:20]}...")
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            if token in sessions:
                user = sessions[token]['user']
                del sessions[token]
                print(f"Logout successful for {user}")
                return jsonify({
                    'success': True,
                    'message': 'Logged out successfully'
                })
        
        return jsonify({
            'success': True,
            'message': 'Logged out (no active session found)'
        })
        
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/v1/auth/status', methods=['GET'])
def status():
    """Handle status check requests"""
    try:
        auth_header = request.headers.get('Authorization', '')
        print(f"Status check with auth: {auth_header[:20]}...")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Missing or invalid authorization header'
            }), 401
        
        token = auth_header[7:]
        if token not in sessions:
            print(f"Status check failed - invalid token")
            return jsonify({
                'success': False,
                'message': 'Session expired or invalid'
            }), 401
        
        # Update last activity
        sessions[token]['last_activity'] = time.time()
        
        session = sessions[token]
        user_input = session['user']
        user_info = users[user_input]
        
        response_data = {
            'success': True,
            'message': 'Session is active',
            'user_info': {
                **user_info,
                'last_activity': time.strftime('%Y-%m-%d %H:%M:%S'),
                'session_duration': f"{int(time.time() - session['created_at'])} seconds"
            },
            'expires_at': 'Never (demo session)'
        }
        
        print(f"Status check successful for {user_input}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Status check error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/v1/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'active_sessions': len(sessions)
    })

@app.route('/v1/users', methods=['GET'])  
def list_users():
    """List available test users"""
    user_list = []
    for username, info in users.items():
        user_list.append({
            'username': username,
            'name': info['name'],
            'email': info['email'],
            'organization': info['organization']
        })
    
    return jsonify({
        'users': user_list,
        'note': 'Use the username and corresponding token for testing'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

if __name__ == '__main__':
    print("=" * 60)
    print("SNC Sample API Server")
    print("=" * 60)
    print("Available test users:")
    for username, info in users.items():
        print(f"  Username: {username}")
        print(f"  Token: {info['token']}")
        print(f"  Name: {info['name']}")
        print()
    
    print("API Endpoints:")
    print("  POST /v1/auth/login")
    print("  POST /v1/auth/logout") 
    print("  GET  /v1/auth/status")
    print("  GET  /v1/health")
    print("  GET  /v1/users")
    print()
    print("Server starting on http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
