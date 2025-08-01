import pytest
import agentspring.tools.business as business

def test_create_event():
    result = business.create_event('Meeting', '2025-01-01T10:00', '2025-01-01T11:00', ['a@b.com'])
    assert result['success']
    assert result['title'] == 'Meeting'

def test_list_events():
    result = business.list_events()
    assert result['success']
    assert isinstance(result['events'], list)

def test_generate_report():
    result = business.generate_report('sales', {'region': 'NA'})
    assert result['success']
    assert 'summary' in result

from unittest.mock import patch, MagicMock

@patch('sqlite3.connect')
def test_create_user(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 42
    result = business.create_user('user', 'e@x.com', 'pw')
    assert result['success']
    assert result['user_id'] == 42

@patch('sqlite3.connect')
def test_update_permissions(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.cursor.return_value = mock_cursor
    result = business.update_permissions('user', ['admin'])
    assert result['success']

@patch('sqlite3.connect', side_effect=Exception('fail'))
def test_create_user_fail(mock_conn):
    with patch('builtins.print'):
        with pytest.raises(Exception):
            business.create_user('user', 'e@x.com', 'pw')

@patch('sqlite3.connect', side_effect=Exception('fail'))
def test_update_permissions_fail(mock_conn):
    with patch('builtins.print'):
        with pytest.raises(Exception):
            business.update_permissions('user', ['admin'])
