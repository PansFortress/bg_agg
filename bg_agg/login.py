from flask_login import LoginManager

from . import app
from .database import session
from .models import Reviewer

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login_get"
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(id):
    return session.query(Reviewer).get(int(id))