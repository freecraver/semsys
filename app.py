from app import app
from flask_assets import Environment, Bundle

#app = Flask(__name__)

if __name__ == '__main__':
    assets = Environment(app)
    assets.url = app.static_url_path
    scss = Bundle('style.scss', filters='pyscss', output='all.css')
    assets.register('scss_all', scss)
    app.run(debug=True)