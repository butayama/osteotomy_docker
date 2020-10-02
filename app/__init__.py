from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_nav import Nav
from flask_pagedown import PageDown
from config import config

bootstrap = Bootstrap()
moment = Moment()
nav = Nav()
pagedown = PageDown()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)
    nav.init_app(app)

    if app.config['SSL_REDIRECT']:
        from flask_talisman import Talisman
        Talisman(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .navs.nav_items import NavItems as NavItems
    nav.register_element('top', NavItems.topbar)

    return app
