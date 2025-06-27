# Snowcell Qwen Model Integration with Aider

Your Snowcell API is OpenAI-compatible but requires proper authentication. Here are the working approaches:

## ✅ **Recommended Solution: Use LiteLLM Directly**

Since your API requires authentication, the best approach is to configure it properly:

### Option 1: Environment Variables
```bash
# Set your actual Snowcell API key (if you have one)
export OPENAI_API_KEY="your-actual-snowcell-token"
export OPENAI_API_BASE="https://qwen-chat-predictor.model-serving.snowcell.app/v1"

# Use with aider
python -m aider --model gpt-3.5-turbo --message "Your question here"
```

### Option 2: Command Line Arguments
```bash
python -m aider \
  --model gpt-3.5-turbo \
  --openai-api-base https://qwen-chat-predictor.model-serving.snowcell.app/v1 \
  --openai-api-key your-actual-snowcell-token \
  --message "Your question here"
```

## 🔧 **API Details**

Your Snowcell API:
- **Endpoint**: https://qwen-chat-predictor.model-serving.snowcell.app/v1
- **Format**: OpenAI-compatible
- **Model**: Qwen/Qwen1.5-0.5B-Chat
- **Authentication**: Required (JWT token format)

## 📝 **Direct API Usage**

If you need to test the API directly:

```python
import requests

response = requests.post(
    'https://qwen-chat-predictor.model-serving.snowcell.app/v1/chat/completions',
    json={
        'model': 'Qwen/Qwen1.5-0.5B-Chat',  # Actual model name
        'messages': [{'role': 'user', 'content': 'What is 2+2?'}]
    },
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-actual-token-here'
    }
)

print(response.json())
```

## 🚨 **Authentication Required**

Your API requires a valid JWT token. The token format must be:
`header.payload.signature` (three parts separated by dots)

Contact your Snowcell provider to get a valid API token.

## 🎯 **Usage Summary**

1. **Get your Snowcell API token** from your provider
2. **Set environment variables** or use command line arguments
3. **Use any OpenAI model name** (like `gpt-3.5-turbo`) - your API will serve the Qwen model
4. **Run aider normally** - it will work with your custom endpoint

Your API is properly OpenAI-compatible and will work great with aider once you have the correct authentication token!
