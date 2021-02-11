import os
import logging

from askbob.action.responder import ResponseService
from askbob.speech.transcriber import Transcriber


def make_transcriber(config: dict, device: int, rate: int, file: str, savepath: str) -> Transcriber:
    """Makes a new transcriber instance from the parameters provided."""

    if 'Listener' not in config:
        raise RuntimeError("No listener configuration provided.")

    if 'model' not in config['Listener']:
        raise RuntimeError("No listener model provided.")

    model_path = config['Listener']['model']
    scorer_path = config['Listener']['scorer'] if 'scorer' in config['Listener'] else ''

    if os.path.isdir(model_path):
        model_path = os.path.join(model_path, 'output_graph.pb')
        scorer_path = os.path.join(model_path, scorer_path)

    return Transcriber(model=model_path, scorer=scorer_path, aggressiveness=config['Listener'].getint(
        'aggressiveness', fallback=1), device_index=device, rate=rate, filename=file, save_path=savepath)


async def interactive_loop(args, config, responder: ResponseService):
    """The main interactive loop for Ask Bob.

    Args:
        args: CLI-provided arguments
        config: config.ini runtime configuration provided parameters
        responder (ResponseService): The response service handling queries
    """

    from askbob.speech.synthesiser import TextToSpeechService
    from askbob.speech.transcriber import TranscriptionEvent
    import halo

    transcriber = make_transcriber(
        config, args.device, args.rate, args.file, args.savepath)
    speaker = TextToSpeechService(config['Speaker']['voice_id'])
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

        else:
            logging.error("Unknown transcription event: " + state)
