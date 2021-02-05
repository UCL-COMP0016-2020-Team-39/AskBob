

def setup(args, config):
    import logging
    import json
    import os
    from askbob.plugin.config import ModelGenerator

    configs = []
    for plugin in os.listdir('plugins'):
        if not plugin.startswith('.') and os.path.isdir(os.path.join('plugins', plugin)):
            try:
                configs.append(
                    json.load(open(os.path.join('plugins', plugin, 'config.json'), 'r')))
                logging.info("Loaded plugin: " + plugin)
            except Exception as e:
                logging.error("Could not load plugin: " + plugin)

    config = json.load(open(args.setup, 'r'))
    config['plugin'] = 'main'
    configs.append(config)

    mg = ModelGenerator()
    mg.generate(configs, os.path.join('data', 'rasa'))
