from askbob.speech.listener.file import FileUtteranceService
from askbob.speech.transcriber import Transcriber, TranscriptionEvent
from sanic import Sanic
from sanic.response import json
import tempfile
import os


def voice_routes(app: Sanic, responder, config: dict):
    # Make transcriber
    if 'Listener' not in config:
        raise RuntimeError(
            "Missing Listener section in the runtime configuration file.")

    if 'model' not in config['Listener']:
        raise RuntimeError(
            "Missing Listener.model in the runtime configuration file.")

    model_path = config['Listener']['model']
    scorer_path = config['Listener'].get('scorer', '')

    transcriber = Transcriber(
        model=model_path, scorer=scorer_path, us=None)

    # Setup voice query handler
    @app.route("/voicequery", methods=['POST', 'OPTIONS'])
    async def voice(request):

        sender = request.form.get('sender')
        if not sender:
            return json({
                "error": "A 'sender' must be provided."
            })

        if not sender.isprintable():
            return json({
                "error": "The sender must contain printable characters."
            })

        if 'speech' not in request.files:
            return json({
                "error": "No speech file provided."
            })

        if len(request.files['speech']) != 1:
            return json({
                "error": "Too many speech files uploaded."
            })

        file = request.files['speech'][0]
        if file.name.split('.')[-1] != 'wav' or file.type != 'audio/wav':
            return json({
                "error": "Incorrect speech file type - it must be audio/wav."
            })

        if len(file.body) >= 10485760:
            return json({
                "error": "The speech file must be <10MiB."
            })

        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(file.body)
        f.close()

        try:
            transcriber.us = FileUtteranceService(filename=f.name, aggressiveness=config['Listener'].getint(
                'aggressiveness', fallback=1))
        except Exception as e:
            transcriber.us = None
            return json({
                "error": str(e)
            })

        for state, text in transcriber.transcribe():
            if state == TranscriptionEvent.END_UTTERANCE:
                os.unlink(f.name)
                transcriber.us = None
                if not text or text.isspace():
                    return json({
                        "query": "",
                        "messages": []
                    })

                return json({
                    "query": text,
                    "messages": [
                        response async for response in responder.handle(text, sender)]
                })

        transcriber.us = None
        return json({
            "error": "Speech transcription failed."
        })
