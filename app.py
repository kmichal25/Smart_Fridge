from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from models import db, User
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tajny_klucz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

CORS(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=3005, debug=True)
