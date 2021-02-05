

def setup(args, main_config):
    import logging
    import json
    import os
    from askbob.plugin.config import ModelGenerator

    plugins_folder = main_config['Plugins']['location']

    configs = []
    for plugin in os.listdir(plugins_folder):
        if not plugin.startswith('.') and os.path.isdir(os.path.join(plugins_folder, plugin)):
            try:
                configs.append(
                    json.load(open(os.path.join(plugins_folder, plugin, 'config.json'), 'r')))
                logging.info("Loaded plugin: " + plugin)
            except:
                logging.error("Could not load plugin: " + plugin)

    if args.setup and args.setup != ".":
        config = json.load(open(args.setup, 'r'))
        config['plugin'] = 'main'
        configs.append(config)

    mg = ModelGenerator()
    mg.generate(configs, main_config['Rasa']['config'],
                main_config['Rasa']['model'])
