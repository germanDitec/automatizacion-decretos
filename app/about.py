from flask import Blueprint, g, render_template, redirect, url_for
from .auth import login_required

bp = Blueprint('about', __name__, url_prefix='/about')

@bp.route('/')
@login_required
def about():
    return render_template('about/about.html')