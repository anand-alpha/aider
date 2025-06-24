"""
SnowCell model integration for aider
"""

import json
import os
import requests
import time
from pathlib import Path


def snowcell_completion(**kwargs):
    """
    Custom completion function for SnowCell models
    This function will be called by litellm for snowcell models
    """
    model = kwargs.get("model", "")
    messages = kwargs.get("messages", [])
    temperature = kwargs.get("temperature", 0.7)
    max_tokens = kwargs.get("max_tokens", 1000)
    stream = kwargs.get("stream", False)

    # Extract model key from model name (handle various formats)
    model_key = (
        model.replace("snowcell:", "").replace("snowcell/", "").replace("snowcell-", "")
    )

    # Load SNC config to get model info
    config_file = Path.home() / ".aider" / "snc_config.json"
    if not config_file.exists():
        raise Exception(
            "SNC not configured. Please run: python -m aider snc --user <user> --token <token>"
        )

    with open(config_file, "r") as f:
        config = json.load(f)

    selected_model = config.get("selected_model")
    if not selected_model:
        raise Exception("No model selected. Use: python -m aider snc <model_key>")

    if selected_model["key"] != model_key:
        raise Exception(
            f"Model '{model_key}' not selected. Current: {selected_model['key']}. "
            f"Use: python -m aider snc {model_key}"
        )

    # Make request to SnowCell endpoint
    payload = {
        "model": selected_model["name"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,  # Our API doesn't support streaming, so always use False
    }

    try:
        response = requests.post(
            selected_model["endpoint"],
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        response_data = response.json()

    except requests.exceptions.RequestException as req_error:
        # Mock response if API fails
        response_data = {
            "id": f"chatcmpl-snowcell-mock-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": selected_model["name"],
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Hello! This is a mock response from SnowCell {model_key} model. (API Error: {str(req_error)})",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": sum(
                    len(msg.get("content", "").split()) for msg in messages
                ),
                "completion_tokens": 20,
                "total_tokens": sum(
                    len(msg.get("content", "").split()) for msg in messages
                )
                + 20,
            },
        }

    # Import after we have response_data to avoid any import issues
    from types import SimpleNamespace

    # Handle response based on streaming mode
    if stream:
        # Create streaming generator
        content = (
            response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        )

        def stream_generator():
            words = content.split()
            for i, word in enumerate(words):
                chunk = SimpleNamespace()
                chunk.choices = [SimpleNamespace()]
                chunk.choices[0].delta = SimpleNamespace()
                chunk.choices[0].delta.content = word + (
                    " " if i < len(words) - 1 else ""
                )
                chunk.choices[0].finish_reason = None
                chunk.id = response_data.get(
                    "id", f"chatcmpl-snowcell-{int(time.time())}"
                )
                chunk.object = "chat.completion.chunk"
                chunk.created = response_data.get("created", int(time.time()))
                chunk.model = response_data.get("model", f"snowcell:{model_key}")
                yield chunk

            # Final chunk with finish_reason
            final_chunk = SimpleNamespace()
            final_chunk.choices = [SimpleNamespace()]
            final_chunk.choices[0].delta = SimpleNamespace()
            final_chunk.choices[0].delta.content = ""
            final_chunk.choices[0].finish_reason = "stop"
            final_chunk.id = response_data.get(
                "id", f"chatcmpl-snowcell-{int(time.time())}"
            )
            final_chunk.object = "chat.completion.chunk"
            final_chunk.created = response_data.get("created", int(time.time()))
            final_chunk.model = response_data.get("model", f"snowcell:{model_key}")
            yield final_chunk

        return stream_generator()
    else:
        # Non-streaming response
        model_response = SimpleNamespace()
        model_response.choices = response_data.get("choices", [])
        model_response.usage = response_data.get("usage", {})
        model_response.id = response_data.get(
            "id", f"chatcmpl-snowcell-{int(time.time())}"
        )
        model_response.object = response_data.get("object", "chat.completion")
        model_response.created = response_data.get("created", int(time.time()))
        model_response.model = response_data.get("model", f"snowcell:{model_key}")
        model_response._hidden_params = {}

        return model_response


def register_snowcell_provider():
    """Register SnowCell provider with litellm"""
    try:
        from aider.llm import litellm

        # Force load litellm module
        litellm._load_litellm()

        # Monkey patch litellm's completion function to handle snowcell models
        original_completion = litellm.completion

        def patched_completion(**kwargs):
            model = kwargs.get("model", "")

            # Check if this is a snowcell model
            if model.startswith("snowcell:") or model in ["qwen", "llama", "mistral"]:
                return snowcell_completion(**kwargs)

            # Otherwise use original completion
            return original_completion(**kwargs)

        # Replace the completion function
        litellm.completion = patched_completion

        # Set up custom provider mappings for reference (be careful about the type)
        if not hasattr(litellm, "custom_provider_map"):
            litellm.custom_provider_map = {}
        elif not isinstance(litellm.custom_provider_map, dict):
            # If it's not a dict, create a new dict
            litellm.custom_provider_map = {}

        # Map our models to the snowcell provider
        snowcell_models = {
            "snowcell:qwen": "snowcell",
            "snowcell:llama": "snowcell",
            "snowcell:mistral": "snowcell",
            "qwen": "snowcell",
            "llama": "snowcell",
            "mistral": "snowcell",
        }

        if isinstance(litellm.custom_provider_map, dict):
            litellm.custom_provider_map.update(snowcell_models)

        return True

    except Exception as e:
        print(f"Warning: Could not register SnowCell provider: {e}")
        return False


# Auto-register when module is imported
register_snowcell_provider()
