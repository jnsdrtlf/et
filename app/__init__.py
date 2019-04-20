import os
import warnings

warnings.filterwarnings('ignore', message='greenlet.greenlet size changed')

from flask import Flask, request, g, redirect, url_for

 
# TODO add option `minimal=False` for things like task
def create_app(root_path, minimal=False):
    app_name = 'minimal_app' if minimal else __name__
    app = Flask(app_name, root_path=root_path)

    config = os.environ.get('CONFIG', default='config/dev.cfg')
    secrets = os.environ.get('SECRETS', default='config/secret.cfg')
    app.config.from_pyfile(os.path.abspath(config))
    app.config.from_pyfile(os.path.abspath(secrets))
    app.secret_key = app.secret_key.encode()
    app.static_url_path = app.config.get('STATIC_FOLDER')
    app.static_folder = os.path.join(app.root_path, app.static_url_path)
    app.template_folder = os.path.join(
        app.root_path, app.config.get('TEMPLATE_FOLDER'))

    from app.models.event import Event
    from app.models.grade import Grade
    from app.models.lesson import Lesson
    from app.models.period import Period
    from app.models.relationships import UserGrade, UserLesson, UserSubject
    from app.models.report import Report
    from app.models.school import School
    from app.models.session import Session
    from app.models.subject import Subject
    from app.models.time import Time
    from app.models.user import User
    from app.models import db

    db.init_app(app)

    if not minimal:
        from app.blueprints.api import v1
        from app.blueprints.api.v1 import user as user_api
        from app.blueprints.api.v1 import lesson as lesson_api
        from app.blueprints.api.v1 import session as session_api
        from app.blueprints import auth
        from app.blueprints import index
        from app.blueprints import user as user
        from app.models.enums import Locale
        from app.models import ma
        from app.i18n import babel, moment
        import app.utils as utils
        from app.utils.tasks import tasks
        babel.init_app(app)
        moment.init_app(app)
        ma.init_app(app)
        db.create_all(app=app)

        @app.after_request
        def call_after_request_callbacks(response):
            for callback in getattr(g, 'after_request_callbacks', ()):
                callback(response)
            return response

        @app.before_request
        def auth_middleware():
            sid = request.cookies.get(
                'sid', default='') or request.values.get('sid')
            session_result = Session.verify(sid)
            if session_result:
                g.session = session_result
                g.locale = g.session.user.locale.value
            else:
                g.session = None
                g.locale = utils.get_best_locale().value

            @utils.after_this_request
            def set_cookie(response):
                if g.session:
                    g.session.set_cookie(response)

        @app.before_request
        def config_middleware():
            try:
                g.school = db.session.query(
                    School).filter(School.id == 1).one()
            except:
                g.school = False
                endpoints = [
                    'static', 'auth.config', None,
                    'school_api1.school_post',
                    'school_api1.school_put'
                ]
                if request.endpoint not in endpoints:
                    app.logger.info('No school found. Redirect to config')
                    return redirect(url_for('auth.config', stage='school'))

        @babel.localeselector
        def get_locale():
            return g.locale

        # ------------
        # API routes
        # ------------
        app.register_blueprint(v1.bp, url_prefix='/api/v1')
        app.register_blueprint(user_api.bp, url_prefix='/api/v1/user')
        app.register_blueprint(session_api.bp, url_prefix='/api/v1/session')
        app.register_blueprint(lesson_api.bp, url_prefix='/api/v1/lesson')

        # ------------
        # Frontend
        # ------------
        app.register_blueprint(auth.bp)
        app.register_blueprint(user.bp, url_prefix='/user')
        app.register_blueprint(index.bp)

        tasks.create_events()

    return app, db
