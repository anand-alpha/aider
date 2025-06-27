"""
Custom LiteLLM provider for Snowcell Qwen endpoint
"""

import json
import litellm
import requests
from litellm import CustomLLM
from typing import Iterator, Union


class SnowcellQwenLLM(CustomLLM):
    def completion(
        self, *args, **kwargs
    ) -> Union[litellm.ModelResponse, Iterator[litellm.ModelResponse]]:
        """Handle completion requests for Snowcell Qwen endpoint"""

        # Extract the messages from kwargs
        messages = kwargs.get("messages", [])
        model = kwargs.get("model", "Qwen/Qwen1.5-0.5B-Chat")
        stream = kwargs.get("stream", False)

        # Remove the provider prefix if present
        if model.startswith("snowcell/"):
            model = model[9:]  # Remove 'snowcell/' prefix

        # Make direct HTTP request to Snowcell endpoint (no auth required)
        url = (
            "https://qwen-chat-predictor.model-serving.snowcell.app/v1/chat/completions"
        )
        headers = {"Content-Type": "application/json"}
        data = {"model": model, "messages": messages, "stream": stream}

        # Add optional parameters
        if "temperature" in kwargs:
            data["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            data["max_tokens"] = kwargs["max_tokens"]

        if stream:
            return self._handle_streaming_response(url, headers, data)
        else:
            return self._handle_non_streaming_response(url, headers, data)

    def streaming(self, *args, **kwargs) -> Iterator[litellm.ModelResponse]:
        """Handle streaming requests - LiteLLM calls this method for streaming"""

        # Extract the messages from kwargs
        messages = kwargs.get("messages", [])
        model = kwargs.get("model", "Qwen/Qwen1.5-0.5B-Chat")

        # Remove the provider prefix if present
        if model.startswith("snowcell/"):
            model = model[9:]  # Remove 'snowcell/' prefix

        # Make direct HTTP request to Snowcell endpoint (no auth required)
        url = (
            "https://qwen-chat-predictor.model-serving.snowcell.app/v1/chat/completions"
        )
        headers = {"Content-Type": "application/json"}
        data = {"model": model, "messages": messages, "stream": True}

        # Add optional parameters
        if "temperature" in kwargs:
            data["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            data["max_tokens"] = kwargs["max_tokens"]

        return self._handle_streaming_response(url, headers, data)

    def _handle_non_streaming_response(self, url, headers, data):
        """Handle non-streaming response"""
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        # Convert response to LiteLLM format
        response_data = response.json()

        # Create ModelResponse object
        model_response = litellm.ModelResponse(
            id=response_data.get("id"),
            object=response_data.get("object"),
            created=response_data.get("created"),
            model=response_data.get("model"),
            choices=response_data.get("choices", []),
            usage=response_data.get("usage", {}),
        )

        return model_response

    def _handle_streaming_response(self, url, headers, data):
        """Handle streaming response"""
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()

        def stream_generator():
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            # Return the raw chunk data - let LiteLLM handle the conversion
                            yield chunk_data
                        except json.JSONDecodeError:
                            continue

        return stream_generator()

    async def acompletion(self, *args, **kwargs) -> litellm.ModelResponse:
        """Async completion - just call sync version for now"""
        return self.completion(*args, **kwargs)


# Create instance and register
snowcell_qwen_llm = SnowcellQwenLLM()

# Register the custom provider
litellm.custom_provider_map = [
    {"provider": "snowcell", "custom_handler": snowcell_qwen_llm}
]
