import pytest
import agentspring.run_tests as run_tests
from unittest.mock import patch, MagicMock

# Test run_command for success and failure
@patch('agentspring.run_tests.subprocess.run')
def test_run_command_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='ok', stderr='')
    result = run_tests.run_command('echo ok', 'desc')
    assert result is True

@patch('agentspring.run_tests.subprocess.run')
def test_run_command_failure(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='fail')
    result = run_tests.run_command('false', 'desc')
    assert result is False

# Patch all subprocess.run and run_command calls in tests to always be mocked, even for coverage/linting, to prevent real subprocesses from running and hanging.

@patch('agentspring.run_tests.subprocess.run')
@patch('agentspring.run_tests.Path.exists', return_value=False)
@patch('agentspring.run_tests.sys.exit')
def test_main_exits_if_not_in_root(mock_exit, mock_exists, mock_subproc):
    run_tests.main()
    assert mock_exit.call_count >= 1

@patch('agentspring.run_tests.subprocess.run')
@patch('agentspring.run_tests.Path.exists', return_value=True)
@patch('agentspring.run_tests.run_command', return_value=True)
@patch('agentspring.run_tests.sys.exit')
def test_main_happy_path(mock_exit, mock_run_command, mock_exists, mock_subproc):
    # All commands succeed, should not exit early
    run_tests.main()
    mock_exit.assert_not_called()

@patch('agentspring.run_tests.subprocess.run')
@patch('agentspring.run_tests.Path.exists', return_value=True)
@patch('agentspring.run_tests.run_command', side_effect=[False, True, True, True, True, True, True, True, True, True])
@patch('agentspring.run_tests.sys.exit')
def test_main_exits_on_failed_install(mock_exit, mock_run_command, mock_exists, mock_subproc):
    run_tests.main()
    mock_exit.assert_called()
