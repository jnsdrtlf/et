from flask import Blueprint, render_template

bp = Blueprint('api', __name__)


@bp.route('/', methods=['GET'])
def index():
    return render_template('api/v1/index.html', title='API v1')
