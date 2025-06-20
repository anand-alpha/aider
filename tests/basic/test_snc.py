"""
Test cases for the SNC (Sync and Connect) functionality
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

from aider.snc import SNCAider, SNCError, handle_snc_command


class TestSNCAider(unittest.TestCase):
    """Test cases for SNCAider class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "snc_config.json"
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_login_success(self):
        """Test successful login"""
        snc = SNCAider()
        snc.config_file = self.config_file
        
        # Test login
        snc.login("testuser@example.com", "test-token-12345")
        
        # Verify config file was created
        self.assertTrue(self.config_file.exists())
        
        # Verify config content
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        self.assertEqual(config['user_input'], "testuser@example.com")
        self.assertEqual(config['token'], "test-token-12345")
        self.assertEqual(config['status'], "logged_in")
    
    def test_login_empty_user(self):
        """Test login with empty user input"""
        snc = SNCAider()
        snc.config_file = self.config_file
        
        with self.assertRaises(SNCError) as context:
            snc.login("", "test-token")
        
        self.assertIn("User input cannot be empty", str(context.exception))
    
    def test_login_empty_token(self):
        """Test login with empty token"""
        snc = SNCAider()
        snc.config_file = self.config_file
        
        with self.assertRaises(SNCError) as context:
            snc.login("testuser", "")
        
        self.assertIn("Token cannot be empty", str(context.exception))
    
    def test_login_whitespace_only(self):
        """Test login with whitespace-only inputs"""
        snc = SNCAider()
        snc.config_file = self.config_file
        
        # Test whitespace-only user input
        with self.assertRaises(SNCError):
            snc.login("   ", "test-token")
        
        # Test whitespace-only token
        with self.assertRaises(SNCError):
            snc.login("testuser", "   ")
    
    def test_logout_success(self):
        """Test successful logout"""
        snc = SNCAider()
        snc.config_file = self.config_file
        
        # First login
        snc.login("testuser", "test-token")
        self.assertTrue(self.config_file.exists())
        
        # Then logout
        snc.logout()
        self.assertFalse(self.config_file.exists())
    
    def test_logout_no_session(self):
        """Test logout when no session exists"""
        snc = SNCAider()
        snc.config_file = self.config_file
        
        # Should not raise exception when no config file exists
        snc.logout()
    
    def test_status_logged_in(self):
        """Test status when logged in"""
        snc = SNCAider()
        snc.config_file = self.config_file
        
        # Login first
        snc.login("testuser@example.com", "test-token")
        
        # Mock io to capture output
        mock_io = MagicMock()
        snc.io = mock_io
        
        snc.status()
        
        # Verify status was called with correct arguments
        mock_io.tool_output.assert_any_call("Status: logged_in")
        mock_io.tool_output.assert_any_call("User: testuser@example.com")
    
    def test_status_not_logged_in(self):
        """Test status when not logged in"""
        snc = SNCAider()
        snc.config_file = self.config_file
        
        # Mock io to capture output
        mock_io = MagicMock()
        snc.io = mock_io
        
        snc.status()
        
        # Verify status was called with correct argument
        mock_io.tool_output.assert_called_with("Status: Not logged in")
    
    def test_get_config_exists(self):
        """Test get_config when config exists"""
        snc = SNCAider()
        snc.config_file = self.config_file
        
        # Login first to create config
        snc.login("testuser", "test-token")
        
        config = snc.get_config()
        self.assertIsNotNone(config)
        self.assertEqual(config['user_input'], "testuser")
        self.assertEqual(config['token'], "test-token")
    
    def test_get_config_not_exists(self):
        """Test get_config when config doesn't exist"""
        snc = SNCAider()
        snc.config_file = self.config_file
        
        config = snc.get_config()
        self.assertIsNone(config)


class TestSNCCommandHandler(unittest.TestCase):
    """Test cases for handle_snc_command function"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "snc_config.json"
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('aider.snc.SNCAider')
    def test_login_command(self, mock_snc_class):
        """Test login command handling"""
        mock_snc = MagicMock()
        mock_snc_class.return_value = mock_snc
        
        argv = ['snc', '--user', 'testuser@example.com', '--token', 'test-token-12345']
        result = handle_snc_command(argv)
        
        self.assertTrue(result)
        mock_snc.login.assert_called_once_with('testuser@example.com', 'test-token-12345')
    
    @patch('aider.snc.SNCAider')
    def test_logout_command(self, mock_snc_class):
        """Test logout command handling"""
        mock_snc = MagicMock()
        mock_snc_class.return_value = mock_snc
        
        argv = ['snc', '--logout']
        result = handle_snc_command(argv)
        
        self.assertTrue(result)
        mock_snc.logout.assert_called_once()
    
    @patch('aider.snc.SNCAider')
    def test_status_command(self, mock_snc_class):
        """Test status command handling"""
        mock_snc = MagicMock()
        mock_snc_class.return_value = mock_snc
        
        argv = ['snc', '--status']
        result = handle_snc_command(argv)
        
        self.assertTrue(result)
        mock_snc.status.assert_called_once()
    
    def test_non_snc_command(self):
        """Test that non-SNC commands return False"""
        argv = ['--model', 'gpt-4']
        result = handle_snc_command(argv)
        self.assertFalse(result)
        
        argv = []
        result = handle_snc_command(argv)
        self.assertFalse(result)
        
        argv = ['init']
        result = handle_snc_command(argv)
        self.assertFalse(result)
    
    def test_login_missing_user(self):
        """Test login command with missing user argument"""
        argv = ['snc', '--token', 'test-token']
        
        with patch('sys.stderr'), self.assertRaises(SystemExit):
            handle_snc_command(argv)
    
    def test_login_missing_token(self):
        """Test login command with missing token argument"""
        argv = ['snc', '--user', 'testuser']
        
        with patch('sys.stderr'), self.assertRaises(SystemExit):
            handle_snc_command(argv)
    
    def test_login_missing_both(self):
        """Test login command with both user and token missing"""
        argv = ['snc']
        
        with patch('sys.stderr'), self.assertRaises(SystemExit):
            handle_snc_command(argv)
    
    @patch('aider.snc.SNCAider')
    def test_snc_error_handling(self, mock_snc_class):
        """Test SNC error handling in command handler"""
        mock_snc = MagicMock()
        mock_snc.login.side_effect = SNCError("Test error")
        mock_snc_class.return_value = mock_snc
        
        argv = ['snc', '--user', 'testuser', '--token', 'test-token']
        
        with patch('sys.stderr'), self.assertRaises(SystemExit):
            handle_snc_command(argv)


if __name__ == '__main__':
    unittest.main()
