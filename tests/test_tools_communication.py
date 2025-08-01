import pytest
import agentspring.tools.communication as comm
from unittest.mock import patch
import os

def test_send_notification():
    with patch('agentspring.tools.communication.send_email', return_value={'success': True}):
        result = comm.send_notification('msg', ['email:test@a.com'])
        assert result['success']
        assert 'results' in result

def test_send_email():
    with patch.dict(os.environ, {"EMAIL_USERNAME": "fakeuser", "EMAIL_PASSWORD": "fakepass"}):
        with patch('smtplib.SMTP') as smtp:
            smtp.return_value.__enter__.return_value.send_message = lambda x: None
            result = comm.send_email('to@a.com', 'sub', 'body', from_email='from@a.com')
            assert result['success']

@patch('agentspring.tools.communication.Client')
@patch('agentspring.tools.communication.TWILIO_AVAILABLE', True)
@patch.dict(os.environ, {'TWILIO_ACCOUNT_SID': 'sid', 'TWILIO_AUTH_TOKEN': 'token'})
def test_send_sms_success(mock_client):
    import agentspring.tools.communication as comm
    mock_cli = mock_client.return_value
    mock_cli.messages.create.return_value.sid = 'sid'
    try:
        result = comm.send_sms('+123', 'hi', from_number='+456')
        print('DEBUG send_sms_success result:', result)
        assert result.get('success', False)
    except Exception as e:
        print('DEBUG send_sms_success exception:', e)
        raise

@patch('agentspring.tools.communication.TWILIO_AVAILABLE', False)
def test_send_sms_unavailable():
    import agentspring.tools.communication as comm
    import pytest
    try:
        with pytest.raises(Exception):
            comm.send_sms('+123', 'hi')
    except Exception as e:
        print('DEBUG send_sms_unavailable exception:', e)
        raise

@patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'http://fake-url'})
@patch('requests.post')
def test_send_slack_message_success(mock_post):
    mock_post.return_value.status_code = 200
    result = comm.send_slack_message('chan', 'msg')
    assert result['success']

@patch('requests.post', side_effect=Exception('fail'))
def test_send_slack_message_failure(mock_post):
    with pytest.raises(Exception):
        comm.send_slack_message('chan', 'msg')

@patch.dict(os.environ, {'DISCORD_WEBHOOK_URL': 'http://fake-url'})
@patch('requests.post')
def test_send_discord_message_success(mock_post):
    mock_post.return_value.status_code = 200
    result = comm.send_discord_message('chan', 'msg')
    assert result['success']

@patch('requests.post', side_effect=Exception('fail'))
def test_send_discord_message_failure(mock_post):
    with pytest.raises(Exception):
        comm.send_discord_message('chan', 'msg')

@patch('agentspring.tools.communication.send_email', return_value={'success': True})
@patch('agentspring.tools.communication.send_sms', return_value={'success': True})
@patch('agentspring.tools.communication.send_slack_message', return_value={'success': True})
@patch('agentspring.tools.communication.send_discord_message', return_value={'success': True})
def test_send_notification_all_channels(mock_discord, mock_slack, mock_sms, mock_email):
    result = comm.send_notification('msg', ['email:test@a.com', 'sms:+123', 'slack:chan', 'discord:chan'])
    assert result['success']
    assert len(result['results']) == 4

@patch('agentspring.tools.communication.send_email', side_effect=Exception('fail'))
def test_send_notification_failure(mock_email):
    result = comm.send_notification('msg', ['email:test@a.com'])
    print('DEBUG send_notification_failure result:', result)
    assert not result.get('success', False)
    # Accept both dict and str error results
    errors = [r['error'] if isinstance(r, dict) and 'error' in r else r for r in result.get('results',{}).values()]
    assert any('fail' in str(e) for e in errors)
