import functools
from flask import (Blueprint, g, current_app, request, render_template, redirect, url_for, flash, session)
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        repass = request.form['repass']
        error = None
        
        db = get_db()
        c = db.cursor()
        c.execute(
            "SELECT usuario_id FROM Usuario WHERE email = ?", (email,)
        )

        if not name or not email or not password or not repass:
            error = "Todos los campos son obligatorios."

        elif password != repass:
            error = "Las contraseñas no coinciden."

        elif not email.endswith('@maipu.cl'):
            error = "No se admiten correos sin el dominio @maipu.cl"

        elif c.fetchone() is not None:
            error = "Usuario con correo {} ya se encuentra registrado.".format(email)

        if error is None:
            c.execute(
                "INSERT INTO Usuario(nombre, email, password) OUTPUT Inserted.usuario_id VALUES (?,?,?)", 
                (name, email, generate_password_hash(password))
            )

            user_id = c.fetchone()[0]
            db.commit()
            session.clear()
            session['user_id'] = user_id
            return redirect(url_for('home.index'))
        
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        error = None
        db = get_db()
        c = db.cursor()

        if not email or not password:
            error = "Todos los campos son requeridos."
        
        c.execute("SELECT * FROM Usuario WHERE email = ?", (email,))

        user = c.fetchone()
        
        if user is None:
            error = "Usuario y/o contraseña incorrecta."

        elif not check_password_hash(user[3], password):
            error = "Usuario y/o contraseña incorrecta."
              
        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('home.index'))    

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM Usuario WHERE usuario_id = ?", (user_id,))
        g.user = c.fetchone()[0]


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
