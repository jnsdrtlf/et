from functools import wraps

from flask import g, redirect, url_for, request

from app.models.enums import Status, Locale


def requires_auth():
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not g.session:
                return redirect(url_for('auth.login_get'))
            else:
                return f(*args, **kwargs)

        return wrapped

    return wrapper


def requires_auth_status():
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not g.session:
                return redirect(url_for('auth.login_get'))
            elif g.session.user.status is not Status.accepted:
                return redirect(url_for('auth.wait'))
            else:
                return f(*args, **kwargs)

        return wrapped

    return wrapper


def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


def get_best_locale():
    """ Get locale

    This function needs to be called in the context of a request.
    """
    _locale = request.accept_languages.best_match(Locale.to_short_list())
    if not _locale:
        _locale = request.accept_languages.best_match(Locale.to_list())

    return Locale(_locale) or Locale.default()
