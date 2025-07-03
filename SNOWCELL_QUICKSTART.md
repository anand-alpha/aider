# Snowcell Quick Start Guide

This guide provides a quick overview of how to get started with Snowcell Chat (snc), the rebranded version of Aider with Snowcell integration.

## Installation

```bash
# Install the package
python -m pip install aider-install
aider-install
```

## Authentication

Before using Snowcell Chat, you need to authenticate:

```bash
# Login with your Snowcell token
snc --login your_token_here

# Check your authentication status
snc --status

# Logout when needed
snc --logout
```

## Basic Usage

Once authenticated, you can use Snowcell Chat with various models:

```bash
# Use the Qwen model (Snowcell's custom model)
snc --model qwen file1.py file2.py

# Alternative syntax
snc --model snowcell/qwen file1.py file2.py

# Use other supported models
snc --model gpt-4o file.py
```

## Features

Snowcell Chat inherits all the powerful features from Aider:

- **Code Understanding**: Works with 100+ programming languages
- **Git Integration**: Automatically commits changes with sensible commit messages
- **Codebase Mapping**: Creates a map of your entire codebase for better context
- **IDE Integration**: Use from within your favorite IDE or editor
- **Images & Web Pages**: Add visual context to your conversations
- **Voice-to-Code**: Request features using your voice
- **Linting & Testing**: Automatically lint and test your code

## Configuration

Snowcell Chat uses configuration files with the `.snc.*` prefix instead of `.aider.*`. Environment variables use the `SNC_*` prefix instead of `AIDER_*`.

## Additional Resources

For more detailed information, refer to:

- [Snowcell Integration Documentation](SNOWCELL_INTEGRATION.md)
- [Snowcell Solution Guide](SNOWCELL_SOLUTION.md)
- [Aider Documentation](https://aider.chat/docs/)

## Support

If you encounter any issues or have questions about Snowcell Chat, please refer to the documentation or contact Snowcell support.