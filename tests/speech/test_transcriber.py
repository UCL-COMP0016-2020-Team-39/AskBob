from askbob.speech.transcriber import Transcriber, TranscriptionEvent


def make_transcriber():
    model_path = 'data/deepspeech-0.9.1-models.pbmm'
    file_path = 'tests/this is a test.wav'

    return Transcriber(model=model_path, scorer='', aggressiveness=1, device_index=None, rate=16000, filename=file_path, save_path='')


def test_transcriber():
    transcriber = make_transcriber()
    transcriptions = transcriber.transcribe()

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is a test'
