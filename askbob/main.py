import os
import logging

from askbob.action.responder import RasaResponseService


def make_transcriber(config, device, rate, file, savepath):
    from askbob.audio.transcriber import Transcriber

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


async def interactive_loop(args, config, responder):
    from askbob.audio.speaker import SpeechService
    from askbob.audio.transcriber import TranscriptionEvent
    import halo

    transcriber = make_transcriber(
        config, args.device, args.rate, args.file, args.savepath)
    speaker = SpeechService(config['Speaker']['voice_id'])
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
                    print("=>", response)
                    speaker.say(response)

        else:
            logging.error("Unknown transcription event: " + state)


def main(args, config):
    responder = RasaResponseService(config['Rasa']['model'])

    if args.serve:
        from sanic import Sanic
        from sanic.response import text, json

        app = Sanic("Ask Bob")

        @app.route("/")
        async def hello(request):
            return text("Hi, there! I think you might be in the wrong place... Bob.")

        @app.route("/query", methods=['POST'])
        async def query(request):
            message = request.form.get('message')
            sender = request.form.get('sender')

            if not message or not sender:
                return json({
                    "error": "Both a 'message' and a 'sender' must be provided."
                })

            if not message.isprintable():
                return json({
                    "error": "The message must contain printable characters."
                })

            if not sender.isprintable():
                return json({
                    "error": "The message must contain printable characters."
                })

            return json({
                "messages": [
                    response async for response in responder.handle(message, sender)]
            })

        logging.info("Running Ask Bob HTTP server.")
        app.run(host=config['Server']['host'],
                port=int(config['Server']['port']))

    else:
        import asyncio
        asyncio.run(interactive_loop(args, config, responder))
