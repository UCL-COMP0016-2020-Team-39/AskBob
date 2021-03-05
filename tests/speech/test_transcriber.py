from askbob.speech.listener.file import FileUtteranceService
from askbob.speech.transcriber import Transcriber, TranscriptionEvent

model = 'data/deepspeech-0.9.1-models.pbmm'
scorer = 'data/deepspeech-0.9.1-models.scorer'


def test_transcriber_without_us():
    transcriber = Transcriber(model=model, scorer='', us=None, save_path='')
    transcriber.transcribe()


def test_transcriber_without_scorer():
    us = FileUtteranceService(
        filename='tests/this is a test.wav', aggressiveness=1)
    transcriber = Transcriber(model=model, scorer='', us=us, save_path='')
    transcriptions = transcriber.transcribe()

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is a test'


def test_transcriber_with_scorer():
    us = FileUtteranceService(
        filename='tests/this is a test.wav', aggressiveness=1)
    transcriber = Transcriber(model=model, scorer=scorer, us=us, save_path='')
    transcriptions = transcriber.transcribe()

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is a test'


def test_transcriber_save(tmp_path):
    d = tmp_path / "transcriber_test"
    d.mkdir()

    us = FileUtteranceService(
        filename='tests/this is a test.wav', aggressiveness=1)
    transcriber = Transcriber(
        model=model, scorer=scorer, us=us, save_path=str(d))
    transcriptions = transcriber.transcribe()

    state, _ = next(transcriptions)
    assert state == TranscriptionEvent.START_UTTERANCE

    state, text = next(transcriptions)
    assert state == TranscriptionEvent.END_UTTERANCE
    assert text == 'this is a test'

    assert len(list(tmp_path.iterdir())) == 1
    assert len(list(d.iterdir())) == 1


def test_transcriber_empty_with_scorer():
    us = FileUtteranceService(filename='tests/empty.wav', aggressiveness=1)
    transcriber = Transcriber(model=model, scorer=scorer, us=us, save_path='')
    transcriptions = transcriber.transcribe()
    assert next(transcriptions, True) == True


def test_transcriber_empty_resampled_with_scorer():
    us = FileUtteranceService(
        filename='tests/empty_44100.wav', aggressiveness=1)
    transcriber = Transcriber(model=model, scorer=scorer, us=us, save_path='')
    transcriptions = transcriber.transcribe()
    assert next(transcriptions, True) == True


def test_transcriber_two_tests_with_scorer():
    us = FileUtteranceService(
        filename='tests/two tests.wav', aggressiveness=1)
    transcriber = Transcriber(model=model, scorer=scorer, us=us, save_path='')
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
    print(7)
    d = tmp_path / "transcriber_test_2"
    d.mkdir()

    us = FileUtteranceService(
        filename='tests/two tests.wav', aggressiveness=1)
    transcriber = Transcriber(
        model=model, scorer=scorer, us=us, save_path=str(d))
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
