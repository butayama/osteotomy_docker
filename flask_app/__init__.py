from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
# from flask_nav import Nav
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
# from flaskext.markdown import Markdown
from config import config
# from flask_consent import Consent

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
# nav = Nav()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config['CONSENT_FULL_TEMPLATE'] = 'consent.html'
    app.config['CONSENT_BANNER_TEMPLATE'] = 'consent_banner.html'
    # consent = Consent(app)
    # consent.add_standard_categories()
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    # nav.init_app(app)
    # Markdown(app, extensions=['fenced_code'])

    if app.config['SSL_REDIRECT']:
        from flask_talisman import Talisman
        Talisman(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # from .navs.nav_items import NavItems as NavItems
    # nav.register_element('top', NavItems.topbar)

    return app
