
if __name__ == '__main__':
    # Parse CLI arguments
    from askbob.util import make_argument_parser
    parser = make_argument_parser()
    args = parser.parse_args()

    # Parse runtime configuration file values
    import configparser
    config = configparser.ConfigParser()
    config.read(args.config)

    if args.setup:
        # Train and setup the assistant
        from .setup import setup
        setup(args, config)
    else:
        # Run the voice assistant
        from askbob.action.responder import RasaResponseService
        responder = RasaResponseService(config['Rasa']['model'])

        if args.serve:
            # Run Ask Bob in server mode
            from .server import serve
            serve(responder, config)
        else:
            # Run Ask Bob in interactive mode
            from askbob.loop import interactive_loop
            import asyncio
            asyncio.run(interactive_loop(args, config, responder))
