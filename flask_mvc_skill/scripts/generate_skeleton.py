import os
import argparse

def create_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_skeleton(project_name):
    base_dir = os.path.join(os.getcwd(), project_name)
    
    if os.path.exists(base_dir):
        print(f"Directory '{project_name}' already exists.")
        # straightforward overwrite check could be added here
    
    create_directory(base_dir)
    
    # Define structure
    dirs = [
        'app',
        'app/models',
        'app/controllers',
        'app/views',
        'app/views/static',
        'app/views/static/css',
        'app/views/static/js',
        'app/views/static/images',
        'app/views/templates',
        'app/views/templates/components',
        'app/views/templates/macros',
        'app/views/templates/main',
        'tests'
    ]
    
    for d in dirs:
        create_directory(os.path.join(base_dir, d))

    # Files content
    
    # 1. requirements.txt
    create_file(os.path.join(base_dir, 'requirements.txt'), 
"""Flask
Flask-SQLAlchemy
Flask-Migrate
python-dotenv
""")

    # 2. run.py
    create_file(os.path.join(base_dir, 'run.py'),
"""import os
from app import create_app

config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True)
""")

    # 3. config.py
    create_file(os.path.join(base_dir, 'config.py'),
"""import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///data-dev.sqlite'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///data.sqlite'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
""")

    # 4. app/__init__.py
    create_file(os.path.join(base_dir, 'app', '__init__.py'),
"""from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__, 
                template_folder='views/templates', 
                static_folder='views/static')
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    # Register Blueprints
    from .controllers.main_controller import main_bp
    app.register_blueprint(main_bp)

    return app
""")

    # 5. app/models/example_model.py
    create_file(os.path.join(base_dir, 'app', 'models', 'user.py'),
"""from .. import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return f'<User {self.username}>'
""")

    # 6. app/models/__init__.py
    create_file(os.path.join(base_dir, 'app', 'models', '__init__.py'), "")

    # 7. app/controllers/main_controller.py
    create_file(os.path.join(base_dir, 'app', 'controllers', 'main_controller.py'),
"""from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html', title="Home")

@main_bp.route('/about')
def about():
    return render_template('main/about.html', title="About Us")
""")

    # 8. app/controllers/__init__.py
    create_file(os.path.join(base_dir, 'app', 'controllers', '__init__.py'), "")

    # 9. Templates
    
    # base.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'base.html'),
"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Flask App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block head %}{% endblock %}
</head>
<body>
    {% include 'components/navbar.html' %}

    <main class="container">
        {% block content %}{% endblock %}
    </main>

    {% include 'components/footer.html' %}

    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
""")

    # components/navbar.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'components', 'navbar.html'),
"""<nav class="navbar">
    <div class="logo">MyApp</div>
    <ul class="nav-links">
        <li><a href="{{ url_for('main.index') }}">Home</a></li>
        <li><a href="{{ url_for('main.about') }}">About</a></li>
    </ul>
</nav>
""")

    # components/footer.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'components', 'footer.html'),
"""<footer class="footer">
    <p>&copy; 2026 My Flask App. All rights reserved.</p>
</footer>
""")

    # macros/forms.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'macros', 'forms.html'),
"""{% macro render_field(name, value='', type='text', placeholder='') %}
<div class="form-group">
    <label for="{{ name }}">{{ name|capitalize }}</label>
    <input type="{{ type }}" name="{{ name }}" value="{{ value }}" placeholder="{{ placeholder }}" class="form-control">
</div>
{% endmacro %}
""")

    # main/index.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'main', 'index.html'),
"""{% extends 'base.html' %}

{% block title %}{{ title }} - MyApp{% endblock %}

{% block content %}
<section class="hero">
    <h1>Welcome to Flask MVC</h1>
    <p>A simple, modular starting point for your next big idea.</p>
    <button class="btn">Get Started</button>
</section>
{% endblock %}
""")

    # main/about.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'main', 'about.html'),
"""{% extends 'base.html' %}

{% block content %}
<section class="about">
    <h1>About Us</h1>
    <p>We are building cool things with Flask.</p>
</section>
{% endblock %}
""")

    # 10. CSS
    create_file(os.path.join(base_dir, 'app', 'views', 'static', 'css', 'style.css'),
"""/* Reset & Basics */
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; background: #f4f4f9; display: flex; flex-direction: column; min-height: 100vh; }

/* Layout */
.container { max-width: 1200px; margin: 0 auto; padding: 20px; flex: 1; }
.navbar { background: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.nav-links { list-style: none; display: flex; gap: 20px; }
.nav-links a { text-decoration: none; color: #333; font-weight: 500; }
.logo { font-size: 1.5rem; font-weight: bold; color: #007bff; }
.footer { background: #333; color: #fff; text-align: center; padding: 1rem; margin-top: auto; }

/* Components */
.btn { display: inline-block; background: #007bff; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; transition: background 0.3s; }
.btn:hover { background: #0056b3; }
""")

    # 11. JS
    create_file(os.path.join(base_dir, 'app', 'views', 'static', 'js', 'main.js'),
"""console.log('Flask MVC App Loaded');
""")

    print(f"Flask MVC Project '{project_name}' generated successfully!")
    print(f"Next steps:")
    print(f"  cd {project_name}")
    print(f"  pip install -r requirements.txt")
    print(f"  python3 run.py")

if __name__ == '__main__':
    parser = argparse.ParameterParser(description='Generate Flask MVC Skeleton')
    parser.add_argument('--name', type=str, default='flask_mvc_app', help='Name of the project directory')
    
    # We'll use a slightly different parsing approach since 'argparse' might not be fully available or robust in all envs without full wrapper, 
    # but standard library argparse is fine.
    # Let's just use sys.argv for simplicity if needed, but argparse is better.
    
    import sys
    # Simple argument parsing manual fallback if needed, but sticking to argparse
    args = parser.parse_args()
    
    generate_skeleton(args.name)
""")

    # Correction: argparse.ParameterParser is not a thing. It's argparse.ArgumentParser
    # I will fix this in the code I write.
    
    final_content = """import os
import argparse
import sys

def create_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_skeleton(project_name):
    base_dir = os.path.join(os.getcwd(), project_name)
    
    if os.path.exists(base_dir):
        print(f"Directory '{project_name}' already exists.")
        # We generally wait for user intervention or just warn, but to keep it safe let's not nuke it unless forced (logic not fully implemented for force, just warn)
        # proceeding might overwrite files. 
    
    create_directory(base_dir)
    
    # Define structure
    dirs = [
        'app',
        'app/models',
        'app/controllers',
        'app/views',
        'app/views/static',
        'app/views/static/css',
        'app/views/static/js',
        'app/views/static/images',
        'app/views/templates',
        'app/views/templates/components',
        'app/views/templates/macros',
        'app/views/templates/main',
        'tests'
    ]
    
    for d in dirs:
        create_directory(os.path.join(base_dir, d))

    # Files content
    
    # 1. requirements.txt
    create_file(os.path.join(base_dir, 'requirements.txt'), 
\"\"\"Flask
Flask-SQLAlchemy
Flask-Migrate
python-dotenv
\"\"\")

    # 2. run.py
    create_file(os.path.join(base_dir, 'run.py'),
\"\"\"import os
from app import create_app

config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True)
\"\"\")

    # 3. config.py
    create_file(os.path.join(base_dir, 'config.py'),
\"\"\"import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \\
        'sqlite:///data-dev.sqlite'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \\
        'sqlite://'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \\
        'sqlite:///data.sqlite'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
\"\"\")

    # 4. app/__init__.py
    create_file(os.path.join(base_dir, 'app', '__init__.py'),
\"\"\"from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__, 
                template_folder='views/templates', 
                static_folder='views/static')
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    # Register Blueprints
    from .controllers.main_controller import main_bp
    app.register_blueprint(main_bp)

    return app
\"\"\")

    # 5. app/models/example_model.py
    create_file(os.path.join(base_dir, 'app', 'models', 'user.py'),
\"\"\"from .. import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return f'<User {self.username}>'
\"\"\")

    # 6. app/models/__init__.py
    create_file(os.path.join(base_dir, 'app', 'models', '__init__.py'), "")

    # 7. app/controllers/main_controller.py
    create_file(os.path.join(base_dir, 'app', 'controllers', 'main_controller.py'),
\"\"\"from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html', title="Home")

@main_bp.route('/about')
def about():
    return render_template('main/about.html', title="About Us")
\"\"\")

    # 8. app/controllers/__init__.py
    create_file(os.path.join(base_dir, 'app', 'controllers', '__init__.py'), "")

    # 9. Templates
    
    # base.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'base.html'),
\"\"\"<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Flask App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block head %}{% endblock %}
</head>
<body>
    {% include 'components/navbar.html' %}

    <main class="container">
        {% block content %}{% endblock %}
    </main>

    {% include 'components/footer.html' %}

    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
\"\"\")

    # components/navbar.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'components', 'navbar.html'),
\"\"\"<nav class="navbar">
    <div class="logo">MyApp</div>
    <ul class="nav-links">
        <li><a href="{{ url_for('main.index') }}">Home</a></li>
        <li><a href="{{ url_for('main.about') }}">About</a></li>
    </ul>
</nav>
\"\"\")

    # components/footer.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'components', 'footer.html'),
\"\"\"<footer class="footer">
    <p>&copy; 2026 My Flask App. All rights reserved.</p>
</footer>
\"\"\")

    # macros/forms.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'macros', 'forms.html'),
\"\"\"{% macro render_field(name, value='', type='text', placeholder='') %}
<div class="form-group">
    <label for="{{ name }}">{{ name|capitalize }}</label>
    <input type="{{ type }}" name="{{ name }}" value="{{ value }}" placeholder="{{ placeholder }}" class="form-control">
</div>
{% endmacro %}
\"\"\")

    # main/index.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'main', 'index.html'),
\"\"\"{% extends 'base.html' %}

{% block title %}{{ title }} - MyApp{% endblock %}

{% block content %}
<section class="hero">
    <h1>Welcome to Flask MVC</h1>
    <p>A simple, modular starting point for your next big idea.</p>
    <button class="btn">Get Started</button>
</section>
{% endblock %}
\"\"\")

    # main/about.html
    create_file(os.path.join(base_dir, 'app', 'views', 'templates', 'main', 'about.html'),
\"\"\"{% extends 'base.html' %}

{% block content %}
<section class="about">
    <h1>About Us</h1>
    <p>We are building cool things with Flask.</p>
</section>
{% endblock %}
\"\"\")

    # 10. CSS
    create_file(os.path.join(base_dir, 'app', 'views', 'static', 'css', 'style.css'),
\"\"\"/* Reset & Basics */
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; background: #f4f4f9; display: flex; flex-direction: column; min-height: 100vh; }

/* Layout */
.container { max-width: 1200px; margin: 0 auto; padding: 20px; flex: 1; }
.navbar { background: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.nav-links { list-style: none; display: flex; gap: 20px; }
.nav-links a { text-decoration: none; color: #333; font-weight: 500; }
.logo { font-size: 1.5rem; font-weight: bold; color: #007bff; }
.footer { background: #333; color: #fff; text-align: center; padding: 1rem; margin-top: auto; }

/* Components */
.btn { display: inline-block; background: #007bff; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; transition: background 0.3s; }
.btn:hover { background: #0056b3; }
\"\"\")

    # 11. JS
    create_file(os.path.join(base_dir, 'app', 'views', 'static', 'js', 'main.js'),
\"\"\"console.log('Flask MVC App Loaded');
\"\"\")

    print(f"Flask MVC Project '{project_name}' generated successfully!")
    print(f"Next steps:")
    print(f"  cd {project_name}")
    print(f"  pip install -r requirements.txt")
    print(f"  python3 run.py")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Flask MVC Skeleton')
    parser.add_argument('--name', type=str, default='flask_mvc_app', help='Name of the project directory')
    args = parser.parse_args()
    
    generate_skeleton(args.name)
"""
