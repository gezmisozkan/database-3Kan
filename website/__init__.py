# Bu init dosyası, website klasörünü bir Python paketi haline getirir.
from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import create_engine

db = SQLAlchemy() #Database objesi oluşturuldu
DB_NAME = "database.db" # Database ismi belirlendi

# MySQL connection string
MYSQL_DB_URI = 'mysql+mysqlconnector://root:1234@localhost/3kan'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Hakan1234'

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # Database bağlantısı yapıldı
    db.init_app(app) # Database objesi app ile ilişkilendirildi 

    # MySQL configuration (create a separate engine)
    mysql_engine = create_engine(MYSQL_DB_URI)
    
    # Blueprints for modularity
    from .views import views
    from .auth import auth


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note 
    with app.app_context():
        db.create_all()
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def create_database(app): # Database yoksa oluşturulacak
        if not path.exists('website/' + DB_NAME):
            db.create_all(app=app)
            print('Created Database!')

    # Attach MySQL engine for direct SQL execution
    app.mysql_engine = mysql_engine
    
    return app