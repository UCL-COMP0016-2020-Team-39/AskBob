
import logging


def main():
    # Parse CLI arguments
    from askbob.util import make_argument_parser
    parser = make_argument_parser()
    args = parser.parse_args()

    # Parse runtime configuration file values
    import configparser
    config = configparser.ConfigParser()

    if not config.read(args.config):
        logging.error(
            f"The runtime configuration file {args.config} could not be loaded.")
        return

    if args.setup:
        # Train and setup the assistant
        from .setup import setup
        setup(args, config)
    else:
        if 'Rasa' not in config or 'model' not in config['Rasa']:
            logging.error(
                "Missing Rasa.model location in the runtime configuration file.")
            return

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


if __name__ == '__main__':
    main()
