#!/bin/bash
# Snowcell Qwen Model Usage with Aider
# 
# Your Snowcell API is OpenAI-compatible and works at:
# https://qwen-chat-predictor.model-serving.snowcell.app/v1
#
# To use it with aider, you need to:
#
# 1. Set up environment variables:
export OPENAI_API_KEY="not-needed"  # Your API doesn't require auth, but aider needs this set
export OPENAI_API_BASE="https://qwen-chat-predictor.model-serving.snowcell.app/v1"

# 2. Use any OpenAI model name (the API will ignore it and use your Qwen model):
python -m aider --model gpt-3.5-turbo --message "What is 2+2?" --no-git --yes

# Alternative: Use openai/ prefix:
python -m aider --model openai/gpt-3.5-turbo --message "What is 2+2?" --no-git --yes

# The model name doesn't matter since your API endpoint serves the Qwen model regardless
# of what model name is requested in the API call.

echo "To use Snowcell with aider:"
echo "1. Set OPENAI_API_KEY=not-needed"
echo "2. Set OPENAI_API_BASE=https://qwen-chat-predictor.model-serving.snowcell.app/v1"
echo "3. Use any OpenAI model name like gpt-3.5-turbo"
