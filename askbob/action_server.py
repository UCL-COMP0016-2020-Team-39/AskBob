

if __name__ == '__main__':
    from .util import setup_logging
    from rasa_sdk.endpoint import run

    setup_logging()

    run("plugins", 5055)
