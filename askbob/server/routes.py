from sanic.response import text, json


def routes(app, responder, plugin_configs):
    @app.route("/", methods=['GET', 'OPTIONS'])
    async def hello(request):
        return text("Hi, there! I think you might be in the wrong place... Bob.")

    async def handle_query(message, sender):
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
                "error": "The sender must contain printable characters."
            })

        return json({
            "query": message,
            "messages": [
                response async for response in responder.handle(message, sender)]
        })

    @app.route("/query", methods=['GET'])
    async def query_get(request):
        message = request.args.get('message')
        sender = request.args.get('sender')

        return await handle_query(message, sender)

    @app.route("/query", methods=['POST', 'OPTIONS'])
    async def query(request):
        message = request.form.get('message')
        sender = request.form.get('sender')

        return await handle_query(message, sender)

    @app.route("/skills", methods=['GET', 'OPTIONS'])
    async def skills(request):
        def get_intent_examples(plugin_config, intent_id):
            for intent in plugin_config['intents']:
                if intent['intent_id'] == intent_id:
                    return intent['examples']

            return []

        return json({
            'plugins': [
                {
                    'plugin': plugin_config['plugin'],
                    'description': plugin_config.get('description', ''),
                    'author': plugin_config.get('author', ''),
                    'icon': plugin_config.get('icon', '')
                }
                for plugin_config in plugin_configs],
            'skills': [
                {
                    'plugin': plugin_config['plugin'],
                    'category': skill.get('category', 'miscellaneous'),
                    'description': skill['description'],
                    'examples': get_intent_examples(plugin_config, skill['intent'])
                }
                for plugin_config in plugin_configs
                for skill in plugin_config['skills']
                if 'description' in skill and skill['intent'] != 'nlu_fallback'
            ]
        })
