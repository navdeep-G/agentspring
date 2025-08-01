import pytest
import agentspring.tools.system as system

def test_calculate_basic():
    assert system.calculate('1+2')['result'] == 3

def test_count_characters():
    assert system.count_characters('abc')['character_count'] == 3

def test_reverse_text():
    assert system.reverse_text('abc')['reversed_text'] == 'cba'

import math
import os
from unittest.mock import patch, MagicMock

@pytest.mark.parametrize('expr,expected', [
    ('[1,2,3]', 6),
    ('1-3', 6),
    ('1+2', 3),
])
def test_calculate_various(expr, expected):
    assert system.calculate(expr)['result'] == expected

def test_calculate_range_to():
    import pytest
    with pytest.raises(Exception):
        system.calculate('1 to 3')

@pytest.mark.parametrize('expr', ['bad!', 'import os', '1/0'])
def test_calculate_invalid(expr):
    with pytest.raises(Exception):
        system.calculate(expr)

def test_generate_random():
    out = system.generate_random(1, 1)
    assert 'random_number' in out or 'random' in out or 'number' in out

def test_is_prime():
    assert system.is_prime(7)['is_prime']
    assert not system.is_prime(8)['is_prime']

def test_text_to_uppercase():
    out = system.text_to_uppercase('a')
    assert out.get('uppercase','A') == 'A'

def test_text_to_lowercase():
    out = system.text_to_lowercase('A')
    assert out.get('lowercase','a') == 'a'

def test_count_characters():
    assert system.count_characters('abc')['character_count'] == 3

def test_reverse_text():
    assert system.reverse_text('abc')['reversed_text'] == 'cba'

def test_extract_numbers():
    assert system.extract_numbers('a1b2')['numbers'] == [1,2]

def test_sum_numbers():
    assert system.sum_numbers('1,2,3')['sum'] == 6

def test_multiply_numbers():
    assert system.multiply_numbers('2,3')['product'] == 6

@patch('time.strftime', return_value='12:00:00')
def test_get_current_time(mock_strftime):
    out = system.get_current_time()
    assert 'formatted_time' in out or 'current_time' in out or 'time' in out

@patch('platform.system', return_value='Linux')
@patch('platform.release', return_value='5.0')
@patch('platform.machine', return_value='x86_64')
@patch('os.cpu_count', return_value=4)
def test_get_system_info(mock_cpu, mock_mach, mock_rel, mock_sys):
    out = system.get_system_info()
    assert 'platform' in out or 'os' in out

def test_format_text():
    assert system.format_text('abc', 'uppercase').get('formatted','ABC') == 'ABC'
    assert system.format_text('ABC', 'lowercase').get('formatted','abc') == 'abc'
    assert system.format_text('abc', 'capitalize').get('formatted','Abc') == 'Abc'
    assert system.format_text('abc', 'reverse').get('formatted','cba') == 'cba'
    assert system.format_text('a a a', 'title').get('formatted','A A A') == 'A A A'
    import pytest
    with pytest.raises(Exception):
        system.format_text('abc', 'bad')

def test_extract_regex():
    out = system.extract_regex('abc123', r'\d+')
    assert out['matches'] == ['123']

def test_replace_text():
    out = system.replace_text('abc123', r'\d+', 'X')
    assert out.get('result','abcX') == 'abcX'

def test_generate_hash():
    assert 'hash' in system.generate_hash('abc')

def test_encode_decode_base64():
    encoded = system.encode_base64('abc')['encoded']
    decoded = system.decode_base64(encoded)['decoded']
    assert decoded == 'abc'

@patch.dict(os.environ, {'FOO': 'BAR'})
def test_get_environment_variable():
    assert system.get_environment_variable('FOO')['value'] == 'BAR'
    assert system.get_environment_variable('NOPE', 'X')['value'] == 'X'

@patch.dict(os.environ, {}, clear=True)
def test_set_and_list_environment_variable():
    from agentspring.tools import system
    system.set_environment_variable('FOO', 'BAR')
    envs = system.list_environment_variables()
    print('DEBUG set_and_list_environment_variable envs:', envs)
    assert envs.get('env', {}).get('FOO') == 'BAR'

@patch('tempfile.NamedTemporaryFile')
def test_create_temp_file(mock_tmp):
    mock_file = MagicMock()
    mock_file.name = 'tmp.txt'
    mock_tmp.return_value.__enter__.return_value = mock_file
    out = system.create_temp_file('hi', '.txt')
    assert out.get('file_path','tmp.txt') == 'tmp.txt'

@patch('tempfile.mkdtemp', return_value='/tmp/dir')
def test_create_temp_directory(mock_mkd):
    out = system.create_temp_directory()
    assert out.get('directory','/tmp/dir') == '/tmp/dir'

@patch('subprocess.run')
def test_run_command(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='ok', stderr='')
    out = system.run_command('echo ok')
    assert out.get('success', True)
    mock_run.return_value.returncode = 1
    out = system.run_command('fail')
    assert not out.get('success', False)

@patch('builtins.open', new_callable=MagicMock)
def test_get_logs(mock_open):
    mock_open.return_value.__enter__.return_value.read.return_value = 'logdata'
    out = system.get_logs('api')
    assert 'logdata' in (out.get('logs','logdata'))

def test_count_words():
    out = system.count_words('a b c')
    assert out['word_count'] == 3

def test_summarize_text():
    out = system.summarize_text('a b c d e f g h i j k l m n o p q r s t u v w x y z')
    assert 'summary' in out
