from datetime import timedelta

from flask import Blueprint, request, jsonify, g, url_for
from werkzeug.exceptions import Unauthorized

from app.models import db
from app.models.enums import Status
from app.models.user import User
from app.models.session import Session
from app.utils.tasks import tasks
from app.utils import requires_auth_status, requires_auth

bp = Blueprint('session_api1', __name__)


def login(email, password, remember: bool, next_url):
    """Login

    This is seperated into a function as this code is also needed during
    signup (see `user_api1.user_post`)
    Important: This function needs to be called within the context of an
    request. Otherwise, accessing `g` and `url_for` wont work.
    """
    try:
        user: User = db.session.query(User).filter(User.email == email).one()
        if user.check_password(password):
            g.session = Session(user, session_only=(not remember))
            g.session.browser = str(request.user_agent.browser or '?')
            g.session.platform = str(request.user_agent.platform or '?')

            db.session.add(g.session)
            db.session.commit()

            expiration_date = g.session.last_use + timedelta(days=60)
            tasks.remove_session.schedule(args=(g.session.id,), eta=expiration_date)

            if user.status is Status.pending:
                next_url = url_for('auth.wait')
            if not user.email_confirmed:
                next_url = url_for('auth.confirm')
            return jsonify({
                'success': True,
                'redirect': next_url,
                'sid': g.session.token})
        else:
            raise Exception()
    except Exception as e:
        return jsonify({'success': False, 'reason': 'credentials'}), 401


@bp.route('/', methods=['POST'])
def session_post():
    """POST /

    Use this route to login a user.
    Required values:
      - `email`
      - `password`

    :return: JSON object with `redirect` url or `reason`
    """
    next_url = url_for('index.index')
    if g.session:
        return jsonify({'redirect': next_url}), 200

    email = request.values.get('email', default='')
    password = request.values.get('password', default='')
    remember = request.values.get('remember', default='off')

    return login(email, password, bool(remember == 'on'), next_url)


@bp.route('/<session_id>', methods=['DELETE'])
@requires_auth()
def session_delete(session_id):
    """DELETE /<session_id>

    Delete a session. Notice: The user rquesting
    this deletion must be the user owning the
    corresponding session.
    :return: Success if session was deleted successfully.
    """
    try:
        session = db.session.query(Session).filter(Session.id.is_(session_id)).one()
        if not session.user_id == g.session.user.id:
            return Unauthorized()

        if session.id == g.session.id:
            g.session = None

        db.session.delete(session)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False}), 404
