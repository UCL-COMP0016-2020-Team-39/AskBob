from askbob.speech.transcriber import Transcriber, TranscriptionEvent

model_path = 'data/deepspeech-0.9.1-models.pbmm'
scorer_path = 'data/deepspeech-0.9.1-models.scorer'
file_path = 'tests/this is a test.wav'


def test_transcriber_without_scorer():
    transcriber = Transcriber(model=model_path, scorer='', aggressiveness=1,
                              device_index=None, rate=16000, filename=file_path, save_path='')
    transcriptions = transcriber.transcribe()

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is a test'


def test_transcriber_with_scorer():
    transcriber = Transcriber(model=model_path, scorer=scorer_path, aggressiveness=1,
                              device_index=None, rate=16000, filename=file_path, save_path='')
    transcriptions = transcriber.transcribe()

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is a test'


def test_transcriber_save(tmp_path):
    d = tmp_path / "transcriber_test"
    d.mkdir()

    transcriber = Transcriber(model=model_path, scorer='', aggressiveness=1,
                              device_index=None, rate=16000, filename=file_path, save_path=str(d))
    transcriptions = transcriber.transcribe()

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is a test'

    assert len(list(tmp_path.iterdir())) == 1
    assert len(list(d.iterdir())) == 1


def test_transcriber_empty_with_scorer():
    transcriber = Transcriber(model=model_path, scorer=scorer_path, aggressiveness=1,
                              device_index=None, rate=16000, filename='tests/empty.wav', save_path='')
    transcriptions = transcriber.transcribe()
    assert next(transcriptions, True) == True


def test_transcriber_empty_resampled_with_scorer():
    transcriber = Transcriber(model=model_path, scorer=scorer_path, aggressiveness=1,
                              device_index=None, rate=44100, filename='tests/empty_44100.wav', save_path='')
    transcriptions = transcriber.transcribe()
    assert next(transcriptions, True) == True


def test_transcriber_two_tests_with_scorer():
    transcriber = Transcriber(model=model_path, scorer=scorer_path, aggressiveness=1,
                              device_index=None, rate=16000, filename='tests/two tests.wav', save_path='')
    transcriptions = transcriber.transcribe()

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is a test'

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is another test'


def test_transcriber_two_tests_with_scorer_save_wav(tmp_path):
    d = tmp_path / "transcriber_test_2"
    d.mkdir()

    transcriber = Transcriber(model=model_path, scorer=scorer_path, aggressiveness=1,
                              device_index=None, rate=16000, filename='tests/two tests.wav', save_path=str(d))
    transcriptions = transcriber.transcribe()

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is a test'

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is another test'

    assert len(list(tmp_path.iterdir())) == 1
    assert len(list(d.iterdir())) == 2
