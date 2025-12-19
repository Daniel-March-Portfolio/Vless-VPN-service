from datetime import datetime


def environment(**options):
    from jinja2 import Environment as JinjaEnvironment

    env = JinjaEnvironment(**options)
    env.globals.update({
        'now': datetime.now,
    })
    return env
