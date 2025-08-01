import pytest
import agentspring.tools.web_search as ws
from unittest.mock import patch, MagicMock

@patch('agentspring.tools.web_search.requests.get')
def test_http_get_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {'Content-Type': 'text/plain'}
    mock_resp.text = 'ok'
    mock_resp.url = 'http://example.com'
    mock_resp.encoding = 'utf-8'
    mock_resp.elapsed.total_seconds.return_value = 0.1
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp
    result = ws.http_get('http://example.com')
    assert result['status_code'] == 200
    assert result['content'] == 'ok'

@patch('agentspring.tools.web_search.requests.get', side_effect=Exception('fail'))
def test_http_get_failure(mock_get):
    with pytest.raises(Exception):
        ws.http_get('http://fail.com')

@patch('agentspring.tools.web_search.requests.post')
def test_http_post_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.headers = {'Content-Type': 'application/json'}
    mock_resp.text = 'created'
    mock_resp.url = 'http://example.com'
    mock_resp.encoding = 'utf-8'
    mock_resp.elapsed.total_seconds.return_value = 0.2
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp
    result = ws.http_post('http://example.com', data={'x': 1})
    assert result['status_code'] == 201
    assert result['content'] == 'created'

@patch('agentspring.tools.web_search.requests.post', side_effect=Exception('fail'))
def test_http_post_failure(mock_post):
    with pytest.raises(Exception):
        ws.http_post('http://fail.com', data={})

@patch('agentspring.tools.web_search.requests.put')
def test_http_put_success(mock_put):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {'Content-Type': 'text/plain'}
    mock_resp.text = 'updated'
    mock_resp.url = 'http://example.com'
    mock_resp.encoding = 'utf-8'
    mock_resp.elapsed.total_seconds.return_value = 0.3
    mock_resp.raise_for_status.return_value = None
    mock_put.return_value = mock_resp
    result = ws.http_put('http://example.com', data={'y': 2})
    assert result['status_code'] == 200
    assert result['content'] == 'updated'

@patch('agentspring.tools.web_search.requests.put', side_effect=Exception('fail'))
def test_http_put_failure(mock_put):
    with pytest.raises(Exception):
        ws.http_put('http://fail.com', data={})

@patch('agentspring.tools.web_search.requests.delete')
def test_http_delete_success(mock_delete):
    mock_resp = MagicMock()
    mock_resp.status_code = 204
    mock_resp.headers = {'Content-Type': 'text/plain'}
    mock_resp.text = ''
    mock_resp.url = 'http://example.com'
    mock_resp.encoding = 'utf-8'
    mock_resp.elapsed.total_seconds.return_value = 0.4
    mock_resp.raise_for_status.return_value = None
    mock_delete.return_value = mock_resp
    result = ws.http_delete('http://example.com')
    assert result['status_code'] == 204

@patch('agentspring.tools.web_search.requests.delete', side_effect=Exception('fail'))
def test_http_delete_failure(mock_delete):
    with pytest.raises(Exception):
        ws.http_delete('http://fail.com')

@patch('agentspring.tools.web_search.requests.get')
@patch('builtins.open')
def test_download_file_success(mock_open, mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.iter_content = lambda chunk_size: [b'data']
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    result = ws.download_file('http://example.com', 'file.txt')
    assert result['success']

@patch('agentspring.tools.web_search.requests.get', side_effect=Exception('fail'))
def test_download_file_failure(mock_get):
    with pytest.raises(Exception):
        ws.download_file('http://fail.com', 'file.txt')
