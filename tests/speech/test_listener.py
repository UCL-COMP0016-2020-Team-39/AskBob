from askbob.speech.listener.mic import MicUtteranceService
from askbob.speech.listener.file import FileUtteranceService

import pytest


def test_mic_utterance_service():
    us = MicUtteranceService()

    assert us.stream.is_active()
    us._destroy()


def test_mic_utterance_service_with_device_index():
    import pyaudio

    pa = pyaudio.PyAudio()
    device_index = next(i for i in range(0, pa.get_host_api_info_by_index(0)['deviceCount'])
                        if pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0)

    us = MicUtteranceService(device_index=device_index)
    assert us.stream.is_active()
    us._destroy()


def test_file_error_dual_channel():
    with pytest.raises(RuntimeError):
        FileUtteranceService(filename='tests/dualchannel.wav')
