#!/usr/bin/env python3
"""
Debug URL construction
"""

from urllib.parse import urljoin

base_url = "http://localhost:5000"

# Test different approaches
print("Testing URL construction:")
print(f"Base URL: {base_url}")
print()

print("Method 1 (current):")
endpoint1 = urljoin(base_url.rstrip('/') + '/', "auth/login")
print(f"  urljoin('{base_url.rstrip('/') + '/'}', 'auth/login') = {endpoint1}")

print("\nMethod 2 (with /v1):")
base_url_v1 = "http://localhost:5000/v1"
endpoint2 = urljoin(base_url_v1.rstrip('/') + '/', "auth/login")
print(f"  urljoin('{base_url_v1.rstrip('/') + '/'}', 'auth/login') = {endpoint2}")

print("\nMethod 3 (manual):")
endpoint3 = f"{base_url}/v1/auth/login"
print(f"  {base_url}/v1/auth/login = {endpoint3}")

print("\nMethod 4 (urljoin with v1):")
endpoint4 = urljoin(base_url, "v1/auth/login")
print(f"  urljoin('{base_url}', 'v1/auth/login') = {endpoint4}")

print(f"\nThe API server expects: {base_url}/v1/auth/login")
