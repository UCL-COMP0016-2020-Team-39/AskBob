

def setup(args, config):
    import json
    from askbob.plugin.config import ModelGenerator

    config = json.load(open(args.setup, 'r'))

    mg = ModelGenerator()
    mg.generate([config], "data/rasa")
