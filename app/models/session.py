import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm.exc import NoResultFound
from flask import Response

from app.models import db


class Session(db.Model):
    """Session

    Sessions are used to identify users.

    A unique token is generated and saved as an http only
    cookie. This token can identify a user.
    """
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    token = db.Column(db.String(64), nullable=False, unique=True)
    session_only = db.Column(db.Boolean, nullable=False, default=True)
    last_use = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, nullable=False, default=False)

    browser = db.Column(db.String(64), nullable=True, unique=False)
    platform = db.Column(db.String(64), nullable=True, unique=False)

    user = db.relationship('User', back_populates='sessions')

    def __init__(self, user, session_only=False):
        self.user_id = user.id
        self.user = user
        self.token = secrets.token_hex(64)
        # session_only has priority. If this is set to True,
        # the expiration date will be ignored.
        self.session_only = session_only
        self.last_use = datetime.now()

    def is_expired(self):
        expiration_date = self.last_use + timedelta(days=60)
        return bool(expiration_date < datetime.today())

    def get_string_cookie(self):
        return f'{self.token}'

    def set_cookie(self, response: Response):
        self.last_use = datetime.now()
        db.session.commit()
        expiration_date = self.last_use + timedelta(days=60)
        cookie_expires = None if self.session_only else expiration_date
        response.set_cookie('sid', self.get_string_cookie(),
                            httponly=True, expires=cookie_expires)

    @staticmethod
    def verify(sid: str):
        if sid:
            # get public token from cookie string
            # check if a session with the public token exists
            try:
                # get session with token that is not revoked
                session = db.session.query(Session) \
                    .filter(Session.token.is_(sid)) \
                    .filter(Session.revoked.is_(False)).one()
                if not session.is_expired():
                    session.last_use = datetime.now()
                    return session
                else:
                    return False
            except NoResultFound:
                return False

        return False

    def __repr__(self):
        return f'<Session {self.user_id} @ {self.token[:8]}>'
