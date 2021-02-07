from askbob.action.responder import ResponseService
import logging


def serve(responder: ResponseService, config: dict):
    from sanic import Sanic
    from sanic.response import text, json

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

    logging.info("Running Ask Bob HTTP server.")
    app.run(host=config['Server']['host'],
            port=int(config['Server']['port']),
            access_log=False)
