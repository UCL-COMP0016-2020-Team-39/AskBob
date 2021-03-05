import logging

from askbob.action.responder import ResponseService
from askbob.speech.transcriber import Transcriber


def make_transcriber(config: dict, device: int, rate: int, filename: str, savepath: str) -> Transcriber:
    """Makes a new transcriber instance from the parameters provided."""

    if 'Listener' not in config:
        raise RuntimeError(
            "Missing Listener section in the runtime configuration file.")

    if 'model' not in config['Listener']:
        raise RuntimeError(
            "Missing Listener.model in the runtime configuration file.")

    model_path = config['Listener']['model']
    scorer_path = config['Listener'].get('scorer', '')

    if filename:
        from askbob.speech.listener.file import FileUtteranceService
        us = FileUtteranceService(filename=filename, aggressiveness=config['Listener'].getint(
            'aggressiveness', fallback=1))
    else:
        from askbob.speech.listener.mic import MicUtteranceService
        us = MicUtteranceService(aggressiveness=config['Listener'].getint('aggressiveness', fallback=1),
                                 device_index=device,
                                 input_rate=rate)

    return Transcriber(model=model_path, scorer=scorer_path, us=us, save_path=savepath)


async def interactive_loop(args, config, responder: ResponseService):
    """The main interactive loop for Ask Bob.

    Args:
        args: CLI-provided arguments
        config: config.ini runtime configuration provided parameters
        responder (ResponseService): The response service handling queries
    """

    if 'TTS' not in config or 'voice_id' not in config['TTS']:
        logging.error(
            "Missing voice_id in the runtime configuration ini file.")
        return

    from askbob.speech.synthesiser import TextToSpeechService
    from askbob.speech.transcriber import TranscriptionEvent
    import halo

    try:
        transcriber = make_transcriber(
            config, args.device, args.rate, args.file, args.savepath)
    except Exception as e:
        logging.error(f"Unable to make the transcriber: {e}")
        return

    speaker = TextToSpeechService(config['TTS']['voice_id'])
    spinner = halo.Halo(spinner='line')

    print("Listening (press Ctrl-C to exit).")
    for state, text in transcriber.transcribe():
        if state == TranscriptionEvent.START_UTTERANCE:
            spinner.start()
        elif state == TranscriptionEvent.END_UTTERANCE:
            spinner.stop()

            if text:
                print("==", text)
                async for response in responder.handle(text):
                    if "text" in response:
                        print("=>", response["text"])
                        speaker.say(response["text"])

            if args.file:
                return
