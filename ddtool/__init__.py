from ddtool.config import Config
from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
load_dotenv()
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate()
bcrypt=Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'


def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    from ddtool.utils.routes import utils
    from ddtool.enbd.routes import enbd
    from ddtool.adcb.routes import adcb
    from ddtool.scb.routes import scb
    from ddtool.users.routes import users
    from ddtool.deem.routes import deem
    from ddtool.alhilal.routes import alhilal
    from ddtool.rak.routes import rak
    from ddtool.upload.routes import upload
    from ddtool.dashboard.routes import dashcharts
    from ddtool.reinstate.routes import reinstate
    from ddtool.adcb_leads.routes import adcb_leads
    from ddtool.api.routes import apidata

    
    app.register_blueprint(utils)
    app.register_blueprint(enbd)
    app.register_blueprint(adcb)
    app.register_blueprint(scb)
    app.register_blueprint(users)
    app.register_blueprint(deem)
    app.register_blueprint(alhilal)
    app.register_blueprint(rak)
    app.register_blueprint(upload)
    app.register_blueprint(dashcharts)
    app.register_blueprint(reinstate)
    app.register_blueprint(adcb_leads)
    app.register_blueprint(apidata)
    return app
