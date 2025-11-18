__version__ = "3.1.1"

# Core imports
import logging
import json

from flask import Flask
from flask_cors import CORS
from flask_mail import Mail

# local application imports
from .config import create_filehandler, create_slackhandler, Config
from meteor.flaskdgraph import DGraph
from meteor.users.authentication import jwt

#  extensions initialization
dgraph = DGraph()
mail = Mail()


# the application factory
def create_app(config_class=Config, config_json=None):

    app = Flask(__name__)

    app.logger.addHandler(create_filehandler())

    if config_json:
        app.config.from_file(config_json, json.load)
    else:
        app.config.from_object(config_class)

    if "TESTING" not in app.config:
        app.config["TESTING"] = False

    if app.config.get("DEBUG_MODE"):
        app.debug = True
        try:
            with open(".git/HEAD") as f:
                git = f.read()
            branch = git.split("/")[-1].strip()
            with open(".git/" + git[5:-1]) as f:
                commit = f.read()
            global __version__
            __version__ += "-" + branch + "-" + commit[:7]
        except:
            pass

    if app.debug:
        app.logger.setLevel(logging.DEBUG)

    if app.config.get("SLACK_LOGGING_ENABLED"):
        try:
            slack_handler = create_slackhandler(app.config.get("SLACK_WEBHOOK"))
            app.logger.addHandler(slack_handler)
            app.logger.error("Initialized Slack Logging!")
        except Exception as e:
            app.logger.error(f"Slack Logging not working: {e}")

    app.config["APP_VERSION"] = __version__

    cors = CORS(
        app,
        resources={
            r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}
        },
    )

    jwt.init_app(app)
    dgraph.init_app(app)
    mail.init_app(app)


    # Blueprints Registration
    from meteor.api.routes import api
    app.register_blueprint(api, url_prefix="/api")

    return app


