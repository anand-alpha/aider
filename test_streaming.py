#!/usr/bin/env python3
"""
Test streaming functionality of the custom Snowcell provider
"""
import sys
import os

sys.path.insert(0, "/home/hac/code/aider")

from aider.snowcell_custom import snowcell_qwen_llm
import litellm


def test_streaming():
    print("Testing streaming completion...")

    messages = [{"role": "user", "content": "Say hello in exactly 5 words."}]

    try:
        # Test streaming using the streaming method directly
        response = snowcell_qwen_llm.streaming(
            model="snowcell/Qwen/Qwen1.5-0.5B-Chat", messages=messages
        )

        print("Streaming response:")
        for chunk in response:
            if hasattr(chunk, "choices") and chunk.choices:
                delta = chunk.choices[0].get("delta", {})
                if "content" in delta:
                    print(delta["content"], end="", flush=True)
        print("\n")

    except Exception as e:
        print(f"Streaming test failed: {e}")
        import traceback

        traceback.print_exc()


def test_litellm_streaming():
    print("Testing LiteLLM streaming...")

    messages = [{"role": "user", "content": "Say hello in exactly 5 words."}]

    try:
        # Test streaming through LiteLLM
        response = litellm.completion(
            model="snowcell/Qwen/Qwen1.5-0.5B-Chat", messages=messages, stream=True
        )

        print("LiteLLM streaming response:")
        for chunk in response:
            if hasattr(chunk, "choices") and chunk.choices:
                delta = chunk.choices[0].get("delta", {})
                if "content" in delta:
                    print(delta["content"], end="", flush=True)
        print("\n")

    except Exception as e:
        print(f"LiteLLM streaming test failed: {e}")
        import traceback

        traceback.print_exc()


def test_non_streaming():
    print("Testing non-streaming completion...")

    messages = [{"role": "user", "content": "Say hello in exactly 5 words."}]

    try:
        # Test non-streaming
        response = snowcell_qwen_llm.completion(
            model="snowcell/Qwen/Qwen1.5-0.5B-Chat", messages=messages, stream=False
        )

        print("Non-streaming response:")
        if hasattr(response, "choices") and response.choices:
            content = response.choices[0].get("message", {}).get("content", "")
            print(content)
        print()

    except Exception as e:
        print(f"Non-streaming test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_non_streaming()
    test_streaming()
    test_litellm_streaming()
