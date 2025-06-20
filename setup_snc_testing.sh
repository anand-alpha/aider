#!/bin/bash

# Setup script for SNC testing

echo "Setting up SNC testing environment..."

# Install Flask for the sample API server
echo "Installing Flask..."
pip3 install flask

echo ""
echo "Setup complete!"
echo ""
echo "To test SNC functionality:"
echo "1. Start the sample API server:"
echo "   python3 sample_api_server.py"
echo ""
echo "2. In another terminal, run the tests:"
echo "   python3 test_snc.py"
echo ""
echo "3. Or test manually:"
echo "   python3 -m aider snc --user user@company.com --token demo-token-12345 --api-url http://localhost:5000"
echo ""
