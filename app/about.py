from flask import Blueprint, g, render_template, redirect, url_for, request, send_from_directory
from .auth import login_required
import openai
import json
openai.api_key = "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"


bp = Blueprint('about', __name__, url_prefix='/about')


@bp.route('/')
@login_required
def about():
    return render_template('about/about.html')


@bp.route('/download')
def download_file():
    plantilla_path = "formato-de-informes.pdf"
    return send_from_directory('media', plantilla_path, as_attachment=True)
