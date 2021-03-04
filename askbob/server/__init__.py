from askbob.server.routes import routes
from askbob.action.responder import ResponseService
import logging
import json as Json


def serve(responder: ResponseService, config: dict, voice: bool = False):
    """Services responses to Ask Bob queries and provides information about loaded skills via RESTful endpoints.

    Args:
        responder (ResponseService): The response service handling queries.
        config (dict): The runtime configuration (usually from config.ini).
    """

    from sanic import Sanic

    plugin_configs = Json.load(open(config['Plugins']['summary'],
                                    'r')) if 'summary' in config['Plugins'] else []

    app = Sanic("Ask Bob", configure_logging=False)

    if config['Server'].get('cors_origins', ''):
        from sanic_cors import CORS
        CORS(app, resources={
            r"/*": {"origins": config['Server']['cors_origins']}
        })

    routes(app, responder, plugin_configs)

    if voice:
        from askbob.server.voice import voice_routes
        voice_routes(app, responder, config)
    else:
        from sanic import response
        @app.route('/voicequery', methods=['POST'])
        def voice_disabled(request):
            return response.json({
                "error": "Voice transcription is disabled on this server."
            }, status=503)

    logging.info("Running Ask Bob HTTP server.")
    app.run(host=config['Server'].get('host', '0.0.0.0'),
            port=config['Server'].getint('port', fallback=8000),
            access_log=False)
