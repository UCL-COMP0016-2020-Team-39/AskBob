from askbob.action.responder import ResponseService
import logging
import json as Json


def serve(responder: ResponseService, config: dict):
    """Services responses to Ask Bob queries and provides information about loaded skills via RESTful endpoints.

    Args:
        responder (ResponseService): The response service handling queries.
        config (dict): The runtime configuration (usually from config.ini).
    """

    from sanic import Sanic
    from sanic.response import text, json

    plugin_configs = Json.load(open(config['Plugins']['Summary'],
                                    'r')) if 'summary' in config['Plugins'] else []

    app = Sanic("Ask Bob", configure_logging=False)

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

    @app.route("/skills")
    async def skills(request):
        def get_intent_examples(plugin_config, intent_id):
            for intent in plugin_config['intents']:
                if intent['intent_id'] == intent_id:
                    return intent['examples']

            return []

        return json({
            plugin_config['plugin']: [
                {
                    'description': skill['description'],
                    'examples': get_intent_examples(plugin_config, skill['intent'])
                }
                for skill in plugin_config['skills']
                if 'description' in skill and skill['intent'] != 'nlu_fallback'
            ]
            for plugin_config in plugin_configs
        })

    logging.info("Running Ask Bob HTTP server.")
    app.run(host=config['Server']['host'],
            port=int(config['Server']['port']),
            access_log=False)
