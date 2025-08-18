# import pytest
# import agentspring.tools.media as media
# from unittest.mock import patch

# def test_analyze_image_unavailable():
#     with patch('agentspring.tools.media.PIL_AVAILABLE', False):
#         with pytest.raises(Exception):
#             media.analyze_image('fake.png')

# @patch('agentspring.tools.media.WHISPER_AVAILABLE', False)
# def test_transcribe_audio_unavailable():
#     with pytest.raises(Exception):
#         media.transcribe_audio('audio.wav')

# @patch('agentspring.tools.media.whisper')
# @patch('agentspring.tools.media.WHISPER_AVAILABLE', True)
# def test_transcribe_audio_success(mock_whisper):
#     import agentspring.tools.media as media
#     mock_model = mock_whisper.load_model.return_value
#     mock_model.transcribe.return_value = {"text": "hello"}
#     try:
#         out = media.transcribe_audio('audio.wav')
#         print('DEBUG transcribe_audio_success result:', out)
#         assert out and out.get('text') == 'hello'
#         assert out and out.get('audio_path') == 'audio.wav'
#     except Exception as e:
#         print('DEBUG transcribe_audio_success exception:', e)
#         raise

# @patch('agentspring.tools.media.PIL_AVAILABLE', True)
# @patch('agentspring.tools.media.Image.open')
# def test_analyze_image_success(mock_open):
#     import agentspring.tools.media as media
#     mock_img = mock_open.return_value
#     mock_img.size = (100, 200)
#     try:
#         out = media.analyze_image('img.png')
#         print('DEBUG analyze_image_success result:', out)
#         assert out and out.get('width') == 100
#         assert out and out.get('height') == 200
#     except Exception as e:
#         print('DEBUG analyze_image_success exception:', e)
#         raise
