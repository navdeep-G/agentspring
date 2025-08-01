import pytest
import agentspring.tools.data_storage as ds
import tempfile
import os

def test_write_and_read_file():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        fname = tf.name
    ds.write_file(fname, 'hello', backup=False)
    out = ds.read_file(fname)
    assert out['content'] == 'hello'
    os.remove(fname)

def test_copy_and_move_file():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        src = tf.name
        tf.write(b'data')
    dst = src + '_copy'
    ds.copy_file(src, dst)
    assert os.path.exists(dst)
    moved = dst + '_moved'
    ds.move_file(dst, moved)
    assert os.path.exists(moved)
    os.remove(src)
    os.remove(moved)

def test_delete_file():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        fname = tf.name
    ds.write_file(fname, 'bye', backup=False)
    ds.delete_file(fname)
    assert not os.path.exists(fname)

import shutil
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

@patch('os.path.exists', return_value=True)
@patch('os.listdir', return_value=['a.txt', '.hidden'])
@patch('os.path.isfile', side_effect=lambda x: x == 'a.txt')
@patch('os.path.isdir', return_value=False)
def test_list_files_basic(mock_isdir, mock_isfile, mock_ls, mock_exists):
    files = ds.list_files('.', pattern='*', include_hidden=True)
    print('DEBUG list_files_basic files:', files)
    assert isinstance(files, dict)
    assert 'files' in files
    assert isinstance(files['files'], list)

@patch('os.remove')
def test_delete_file_recursive(mock_remove):
    ds.delete_file('fake.txt', recursive=False)
    mock_remove.assert_called_once()

@patch('shutil.rmtree')
def test_delete_file_recursive_dir(mock_rmtree):
    with patch('os.path.isdir', return_value=True):
        ds.delete_file('dir', recursive=True)
        mock_rmtree.assert_called_once()

@patch('shutil.copy2')
def test_copy_file(mock_copy):
    ds.copy_file('src', 'dst', overwrite=True)
    mock_copy.assert_called_once()

@patch('shutil.move')
def test_move_file(mock_move):
    ds.move_file('src', 'dst', overwrite=True)
    mock_move.assert_called_once()

@patch('os.makedirs')
def test_create_directory(mock_makedirs):
    ds.create_directory('dir', parents=True)
    mock_makedirs.assert_called_once()

@patch('os.stat')
@patch('os.path.getsize', return_value=123)
def test_get_file_info(mock_size, mock_stat):
    mock_stat.return_value = MagicMock(st_mode=33188, st_size=123, st_mtime=1, st_ctime=1)
    info = ds.get_file_info('file.txt')
    assert 'size' in info

@patch('zipfile.ZipFile')
@patch('builtins.open', new_callable=mock_open)
def test_compress_file(mock_open_file, mock_zipfile):
    from agentspring.tools import data_storage as ds
    mock_zip = mock_zipfile.return_value.__enter__.return_value
    ds.compress_file(['a.txt'], 'archive.zip', format='zip')
    print('DEBUG compress_file called:', mock_zip.write.call_args_list)
    mock_zip.write.assert_any_call('a.txt', 'a.txt')

@patch('zipfile.ZipFile')
@patch('os.path.exists', return_value=True)
@patch('os.path.isdir', return_value=False)
@patch('os.path.isfile', return_value=True)
def test_extract_archive(mock_isfile, mock_isdir, mock_exists, mock_zip):
    from agentspring.tools import data_storage as ds
    mock_zip_instance = mock_zip.return_value.__enter__.return_value
    ds.extract_archive('archive.zip', 'outdir')
    print('DEBUG extract_archive called:', mock_zip_instance.extractall.call_args_list)
    try:
        mock_zip_instance.extractall.assert_called_once_with('outdir')
    except AssertionError as e:
        print('DEBUG test_extract_archive AssertionError:', e)
        raise

@patch('builtins.open', new_callable=mock_open, read_data='col1,col2\n1,2')
def test_read_csv(mock_file):
    result = ds.read_csv('file.csv')
    assert 'data' in result
    assert 'header' in result

@patch('builtins.open', new_callable=mock_open)
def test_write_csv(mock_file):
    ds.write_csv('file.csv', data=[[1,2],[3,4]], headers=['a','b'])
    mock_file.assert_called_once()

@patch('builtins.open', new_callable=mock_open, read_data='{"a": 1}')
def test_read_json(mock_file):
    out = ds.read_json('file.json')
    assert out['a'] == 1

@patch('builtins.open', new_callable=mock_open)
def test_write_json(mock_file):
    ds.write_json('file.json', {'a': 1})
    mock_file.assert_called_once()

@patch('agentspring.tools.data_storage.PDF_AVAILABLE', True)
@patch('agentspring.tools.data_storage.PyPDF2.PdfReader')
@patch('builtins.open', new_callable=mock_open, read_data=b'data')
def test_read_pdf(mock_file, mock_reader):
    import agentspring.tools.data_storage as ds
    mock_reader.return_value.pages = [MagicMock()]
    mock_reader.return_value.pages[0].extract_text.return_value = 'PDFTEXT'
    try:
        out = ds.read_pdf('file.pdf')
        print('DEBUG read_pdf result:', out)
        assert out and 'PDFTEXT' in out.get('text','')
    except Exception as e:
        print('DEBUG read_pdf exception:', e)
        raise

@patch('agentspring.tools.data_storage.Image.open')
@patch('agentspring.tools.data_storage.pytesseract.image_to_string', return_value='OCRTEXT')
def test_extract_text(mock_ocr, mock_img):
    import agentspring.tools.data_storage as ds
    try:
        out = ds.extract_text('file.png')
        print('DEBUG extract_text result:', out)
        assert out and 'OCRTEXT' in out.get('text','')
    except Exception as e:
        print('DEBUG extract_text exception:', e)
        raise

@patch('sqlite3.connect')
def test_create_contact(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    mock_cursor.execute.return_value = None
    mock_cursor.lastrowid = 1
    result = ds.create_contact('a','b','c')
    assert result['success']

@patch('sqlite3.connect')
def test_update_lead(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
    mock_cursor.execute.return_value = None
    result = ds.update_lead('id', {'foo': 'bar'})
    assert result['success']
