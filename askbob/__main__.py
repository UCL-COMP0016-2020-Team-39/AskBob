from .main import main
from .setup import setup


if __name__ == '__main__':
    from askbob.util import make_argument_parser
    parser = make_argument_parser()
    args = parser.parse_args()

    import configparser
    config = configparser.ConfigParser()
    config.read(args.config)

    if args.setup:
        setup(args, config)
    else:
        main(args, config)
