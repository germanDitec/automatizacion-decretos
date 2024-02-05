import functools
from flask import (Blueprint, g, current_app, request,
                   render_template, redirect, url_for, flash, session)
from flask_mail import Message, Mail
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db
import uuid
import time


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        repass = request.form['repass']
        error = None

        db, c = get_db()
        c.execute("SELECT usuario_id FROM Usuario WHERE email = %s", (email,))

        if not name or not email or not password or not repass:
            error = "Todos los campos son obligatorios."

        elif password != repass:
            error = "Las contraseñas no coinciden."

        elif not email.endswith('@maipu.cl'):
            error = "No se admiten correos sin el dominio @maipu.cl"

        elif c.fetchone() is not None:
            error = "Usuario con correo {} ya se encuentra registrado.".format(
                email)

        if error is None:
            c.execute(
                "INSERT INTO usuario(nombre, email, password) VALUES (%s, %s, %s) RETURNING usuario_id",
                (name, email, generate_password_hash(password))
            )

            user_id = c.fetchone()[0]
            db.commit()

            verification_token = str(uuid.uuid4())
            c.execute(
                "UPDATE usuario SET verification_token = %s WHERE usuario_id = %s",
                (verification_token, user_id)
            )
            db.commit()
            send_verification_email(email, name, verification_token)

            flash('Se ha enviado un correo de verificación al usuario.', 'info')
            return redirect(url_for('auth.login'))

        flash(error, 'error')

    return render_template('auth/register.html')


def send_verification_email(email, name, token):

    mail = Mail()
    msg = Message(
        'Verifica tu cuenta en la App de Generador de Decretos', recipients=[email])
    verification_url = url_for('auth.verify', token=token, _external=True)
    msg.body = f'Hola {name}, Gracias por registrarte en la App de Generador de Decretos. Por favor, confirma tu cuenta haciendo click en el siguiente link: {verification_url}'

    mail.send(msg)


@bp.route('/verify/<token>')
def verify(token):
    db, c = get_db()

    c.execute(
        "SELECT usuario_id FROM Usuario WHERE verification_token = %s", (token,))
    user = c.fetchone()

    success = False
    if user is not None:
        c.execute(
            "UPDATE usuario SET verified = TRUE, verification_token = NULL WHERE usuario_id = %s", (user[0],))
        db.commit()
        success = True

        session.clear()

    return render_template('auth/verify_email.html', success=success)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        error = None
        db, c = get_db()

        if not email or not password:
            error = "Todos los campos son requeridos."

        c.execute("SELECT * FROM Usuario WHERE email = %s", (email,))

        user = c.fetchone()

        if user is None:
            error = "Usuario y/o contraseña incorrecta."

        if not user[5]:
            error = "El correo ingresado no está verificado."

        elif not check_password_hash(user[3], password):
            error = "Usuario y/o contraseña incorrecta."

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('home.index'))

        flash(error, 'error')

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db, c = get_db()
        c.execute("SELECT * FROM Usuario WHERE usuario_id = %s", (user_id,))
        user = c.fetchone()

        if user is not None and user[5]:
            g.user = user
        else:
            g.user = None


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
