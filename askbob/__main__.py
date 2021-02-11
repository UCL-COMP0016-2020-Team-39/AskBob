
if __name__ == '__main__':
    from askbob.util import make_argument_parser
    parser = make_argument_parser()
    args = parser.parse_args()

    import configparser
    config = configparser.ConfigParser()
    config.read(args.config)

    if args.setup:
        from .setup import setup
        setup(args, config)
    else:
        from askbob.action.responder import RasaResponseService
        responder = RasaResponseService(config['Rasa']['model'])

        if args.serve:
            from .server import serve
            serve(responder, config)
        else:
            from askbob.loop import interactive_loop
            import asyncio
            asyncio.run(interactive_loop(args, config, responder))
