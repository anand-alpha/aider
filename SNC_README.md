# SNC (Sync and Connect) Command Implementation

This implementation adds a new `aider snc` command for web app integration with API support for login, logout, and status operations.

## Features

- **Login**: Authenticate with your company's API using user credentials and token
- **Logout**: Invalidate session and clear local credentials
- **Status**: Check current login status and session validity with API
- **API Integration**: Full HTTP API integration with error handling
- **Local Config**: Secure local storage of session information
- **Custom API URL**: Support for different API endpoints

## Installation

1. The SNC module is already integrated into aider
2. For testing, install Flask for the sample API server:
   ```bash
   pip3 install flask
   ```

## Usage

### Basic Commands

```bash
# Login to your company's API
python3 -m aider snc --user <username> --token <auth_token>

# Check login status
python3 -m aider snc --status

# Logout
python3 -m aider snc --logout

# Get help
python3 -m aider snc --help
```

### Advanced Options

```bash
# Login with custom API URL
python3 -m aider snc --user user@company.com --token your-token --api-url https://api.yourcompany.com/v1

# Set custom timeout (default: 30 seconds)
python3 -m aider snc --user user@company.com --token your-token --timeout 60
```

## Testing

### 1. Start the Sample API Server

In one terminal:

```bash
python3 sample_api_server.py
```

The server will start on `http://localhost:5000` with these test accounts:

| Username          | Token             | Name       |
| ----------------- | ----------------- | ---------- |
| user@company.com  | demo-token-12345  | John Doe   |
| admin@company.com | admin-token-67890 | Jane Admin |
| developer         | dev-token-abcdef  | Dev User   |

### 2. Run Tests

In another terminal:

```bash
# Run comprehensive test suite
python3 test_snc.py

# Or test manually
python3 -m aider snc --user user@company.com --token demo-token-12345 --api-url http://localhost:5000
python3 -m aider snc --status --api-url http://localhost:5000
python3 -m aider snc --logout --api-url http://localhost:5000
```

## API Endpoints

The SNC command expects your company's API to implement these endpoints:

### POST /v1/auth/login

**Request:**

```json
{
  "user_input": "user@company.com",
  "token": "auth-token",
  "client": "aider",
  "timestamp": 1640995200
}
```

**Response (Success):**

```json
{
  "success": true,
  "message": "Login successful",
  "session_token": "uuid-session-token",
  "user_info": {
    "name": "John Doe",
    "email": "user@company.com",
    "organization": "Your Company"
  }
}
```

**Response (Error):**

```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

### POST /v1/auth/logout

**Headers:**

```
Authorization: Bearer <session_token>
```

**Response:**

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### GET /v1/auth/status

**Headers:**

```
Authorization: Bearer <session_token>
```

**Response:**

```json
{
  "success": true,
  "message": "Session is active",
  "user_info": {
    "name": "John Doe",
    "email": "user@company.com",
    "last_activity": "2023-12-31 23:59:59"
  },
  "expires_at": "2024-01-01 23:59:59"
}
```

## Configuration

Session data is stored in `~/.aider/snc_config.json`:

```json
{
  "user_input": "user@company.com",
  "token": "auth-token",
  "status": "logged_in",
  "session_token": "api-session-token",
  "user_info": {
    "name": "John Doe",
    "email": "user@company.com",
    "organization": "Your Company"
  },
  "login_time": 1640995200,
  "api_response": { ... }
}
```

## Customization for Your Company

### 1. Update API Base URL

Modify the default API URL in `aider/snc.py`:

```python
# Change this line in SNCAPIClient.__init__
self.base_url = base_url or "https://api.yourcompany.com/v1"
```

### 2. Customize Authentication

Update the login payload in `SNCAPIClient.login()`:

```python
payload = {
    "user_input": user_input,
    "token": token,
    "client": "aider",
    "company_id": "your-company-id",  # Add company-specific fields
    "app_version": "1.0",
    # Add other required fields
}
```

### 3. Add Custom Headers

Modify the session headers in `SNCAPIClient.__init__`:

```python
self.session.headers.update({
    'Content-Type': 'application/json',
    'User-Agent': 'Aider-SNC/1.0',
    'X-Company-API-Key': 'your-api-key',  # Add company headers
    'X-Client-Version': '1.0'
})
```

## Error Handling

The SNC command handles various error scenarios:

- **Network errors**: Connection timeouts, DNS failures
- **API errors**: 401 Unauthorized, 403 Forbidden, 500 Internal Server Error
- **Authentication errors**: Invalid credentials, expired sessions
- **Input validation**: Empty user input, invalid tokens
- **Configuration errors**: Missing config files, JSON parsing errors

## Security Considerations

- **Tokens**: Authentication tokens are stored locally in `~/.aider/snc_config.json`
- **Session Management**: API sessions are validated on each status check
- **HTTPS**: Use HTTPS endpoints in production for secure communication
- **Token Rotation**: Implement token refresh if your API supports it

## Integration with Aider

The SNC command is integrated into aider's main command processing in `aider/main.py`. It's handled before regular aider processing, allowing it to work independently.

## Files

- `aider/snc.py` - Main SNC implementation
- `sample_api_server.py` - Sample API server for testing
- `test_snc.py` - Comprehensive test suite
- `setup_snc_testing.sh` - Setup script for testing environment

## Support

For issues or questions about the SNC implementation:

1. Check the test output for detailed error messages
2. Verify your API endpoints match the expected format
3. Test with the sample API server first
4. Check network connectivity and API server availability
