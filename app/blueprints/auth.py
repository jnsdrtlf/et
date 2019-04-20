from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import and_
from werkzeug.exceptions import Unauthorized, Forbidden, NotFound
import urllib.parse

from flask import Blueprint, request, jsonify, g, redirect, render_template, flash, url_for
from flask_babel import gettext

from app.models.enums import Status, Role
from app.models.user import User
from app.models.subject import Subject
from app.models.grade import Grade
from app.models import db
from app.utils import requires_auth
import app.utils.tasks.mail as mail

bp = Blueprint('auth', __name__)


@bp.route('/signup', methods=['GET'])
def signup_get():
    """GET /signup

    This route only works if the user is not yet authenticated.
    The user will be redirected to next_url otherwise.
    :return: render_template or redirect
    """
    next_url = url_for('index.index')
    if g.session:
        flash(gettext('You are already logged in'), 'success')
        return redirect(next_url)

    return render_template('sites/auth/signup.html', title=gettext('Signup'))


@bp.route('/login', methods=['GET'])
def login_get():
    """GET /login

    This route only works if the user is not yet authenticated.
    The user will be redirected to next_url otherwise.
    :return: render_template or redirect
    """
    next_url = url_for('index.index')
    if g.session:
        flash(gettext('You are already logged in'), 'success')
        return redirect(next_url)

    return render_template('sites/auth/login.html', title=gettext('Login'))


@bp.route('/login', methods=['POST'])
def login_post():
    """POST /login

    Deprecated. Use the api backend (`session_api1.session_post`) to 
    create a new session and log in.
    """
    return redirect(url_for('session_api1.session_post'))


@bp.route('/auth/reset', methods=['GET'])
def reset_get():
    """GET /auth/reset?token=<string:token>

    Reset password route. If a valid token is provided,
    the password can be reset. If no token is provided,
    the email textbox will be rendered to request a new
    reset link via email.
    :return: Template for password reset
    """
    next_url = url_for('index.index')
    if g.session:
        flash(gettext('You are already logged in'), 'success')
        return redirect(next_url)

    token = request.args.get('token')
    if token:
        try:
            user = db.session.query(User) \
                .filter((User.password_token == token) & User.reset_active) \
                .one()
            if user.is_reset_expired():
                return NotFound()

            return render_template('sites/auth/reset.html',
                                   title=gettext('Reset'),
                                   password=True, password_token=token)
        except NoResultFound:
            return NotFound()
    else:
        return render_template('sites/auth/reset.html',
                               title=gettext('Reset'),
                               email=True, password=False)


@bp.route('/auth/reset-status')
def reset_status():
    """GET /auth/reset-status

    Simple status page for password reset.
    """
    return render_template(
        'sites/auth/reset_status.html', title=gettext('Reset'),
        sent=request.values.get('sent', default=False),
        success=request.values.get('success', default=False))


@bp.route('/auth/reset', methods=['POST'])
def reset_post():
    """POST /auth/reset

    Request a password reset link via email or
    reset the password if a token is specified.
    :return:
    """
    if g.session:
        # User is already authenticated
        return jsonify({'redirect': url_for('index.index')})

    form = request.values.get('form', default='email')
    token = request.values.get('token', default='')
    email = request.values.get('email', default='')
    password = request.values.get('password', default='')

    if form == 'password':
        try:
            user: User = db.session.query(User) \
                .filter((User.password_token == token) & User.reset_active) \
                .one()
            if user.is_reset_expired():
                return jsonify({'success': False, 'reason': 'expired'}), 401

            if len(password) < 8:
                return jsonify({'success': False, 'reason': 'password'}), 401

            user.set_password(password)
            db.session.commit()
            next_url = url_for('auth.reset_status', success=True)
            return jsonify({'success': True, 'redirect': next_url})
        except NoResultFound:
            return jsonify({'success': False, 'reason': 'token not found'}), 401
    else:
        try:
            user: User = db.session.query(User) \
                .filter(User.email == email).one()
            user.reset_password()
            db.session.commit()

            reset_url = urllib.parse.urljoin(
                request.host_url,
                url_for('auth.reset_get', token=user.password_token))
            kwargs = {
                'subject': gettext('Reset Password'),
                'body': reset_url,
                'recipients': [user.email]
            }
            mail.send_mail(**kwargs)
            next_url = url_for('auth.reset_status', sent=True)
            return jsonify({'success': True, 'redirect': next_url})
        except NoResultFound:
            return jsonify({'success': False, 'reason': 'email'}), 401


@bp.route('/auth/confirm', methods=['GET'])
@requires_auth()
def confirm():
    """GET /auth/confirm

    Confirm the valid email address. The token must
    be valid.
    :return: redirect if successful
    """
    if g.session.user.email_confirmed:
        return redirect(url_for('index.index'))

    token = request.args.get('token')
    if token:
        try:
            user: User = db.session.query(User) \
                .filter(User.confirmation_token == token).one()

            user.email_confirmed = True
            user.confirmation_token = None
            db.session.merge(user)
            db.session.commit()

            return render_template('sites/auth/confirm.html',
                                   title=gettext('Confirm Email'),
                                   sent=False, success=True), 200
        except NoResultFound:
            return render_template('sites/auth/confirm.html',
                                   title=gettext('Confirm Email'),
                                   sent=False, success=False), 401
    else:
        return render_template('sites/auth/confirm.html',
                               title=gettext('Confirm Email'), sent=True), 200


@bp.route('/auth/wait')
@requires_auth()
def wait():
    if g.session.user.status is Status.accepted:
        return redirect(url_for('index.index'))

    return render_template('sites/auth/wait.html',
                           title=gettext('Wait'),
                           status=g.session.user.status.value)


@bp.route('/logout')
def logout():
    if g.session:
        g.session.revoked = True
        db.session.commit()
        g.session = None

    return redirect(url_for('index.index'))


@bp.route('/config', methods=['GET'])
def config():
    if g.school:
        return redirect(url_for('index.index'))

    stage = request.args.get('stage', 'school')
    if not g.school:
        pass
        #stage = 'school'

    template = 'sites/auth/config-%s.html'

    if stage in ['school', 'admin', 'subjects', 'time', 'grades']:
        return render_template(template % stage, title=gettext('Config'))
    else:
        return NotFound()


"""@bp.route('/config', methods=['POST'])
@requires_auth()
def config_post():
    if g.session.user.role != Role.admin \
            and g.session.user.status != Status.accepted:
        return Forbidden()

    name = request.values.get('name', '')
    subjects = request.values.getlist('subjects[]')
    grades = request.values.getlist('grades[]')

    g.config = Config()
    g.config.id = 1
    g.config.school_name = name
    db.session.merge(g.config)

    for subject in subjects:
        _subject = Subject()
        _subject.school_id = g.school.id
        _subject.name = subject
        db.session.add(_subject)

    for grade in grades:
        _grade = Grade()
        _grade.school_id = g.school.id
        _grade.name = grade
        db.session.add(_grade)

    db.session.commit()

    return jsonify({'success': True, 'redirect': url_for('index.index')})
"""