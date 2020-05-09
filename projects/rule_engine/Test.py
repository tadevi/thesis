from rule_engine.HandleStream import HandleStream

configs = {
    'url': 0,
    'modules': [
        {
            'name': 'DisplayStream',
            'package': 'rule_engine',
            'configs': {}
        },
        {
            'name': 'human_detection',
            'package': 'modules.image',
            'configs': {}
        }
    ]
}


def run():
    print('run')
    handle_stream = HandleStream(configs)
    handle_stream.run()
