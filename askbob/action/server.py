

if __name__ == '__main__':
    import sys
    from askbob.util import setup_logging
    from rasa_sdk.endpoint import run

    setup_logging()

    run(sys.argv[1], sys.argv[2])
