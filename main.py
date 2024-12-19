from flask import Flask

from auth.views import auth_blueprint
from airport.views import airport_blueprint
from admin.views import admin_blueprint


app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdg3456tyhj4ghdjhbh34b65hj3btghjefdbg465y56'
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(airport_blueprint, url_prefix='/')
