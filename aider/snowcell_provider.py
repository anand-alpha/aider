"""
Simple Snowcell provider that works without authentication.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional


def register_snowcell_provider():
    """Register Snowcell as a custom provider with litellm"""
    try:
        from aider.llm import litellm

        # Force load litellm
        if hasattr(litellm, "_load_litellm"):
            litellm._load_litellm()

        # Add custom provider function
        def snowcell_chat_completion(
            model: str, messages: List[Dict[str, str]], api_base: str = None, **kwargs
        ):
            """Custom Snowcell completion function"""

            # Default API base
            if not api_base:
                api_base = os.getenv(
                    "SNOWCELL_API_BASE",
                    "https://qwen-chat-predictor.model-serving.snowcell.app/v1",
                )

            url = f"{api_base}/chat/completions"

            # Map model name to actual model
            actual_model = "Qwen/Qwen1.5-0.5B-Chat"

            payload = {"model": actual_model, "messages": messages, "stream": False}

            # Add optional parameters
            for key in ["max_tokens", "temperature", "top_p"]:
                if key in kwargs:
                    payload[key] = kwargs[key]

            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            return response.json()

        # Register the custom provider
        litellm.custom_provider_map = getattr(litellm, "custom_provider_map", {})
        litellm.custom_provider_map["snowcell"] = snowcell_chat_completion

        print("✅ Snowcell provider registered successfully")
        return True

    except Exception as e:
        print(f"❌ Failed to register Snowcell provider: {e}")
        return False


# Auto-register when imported
register_snowcell_provider()
