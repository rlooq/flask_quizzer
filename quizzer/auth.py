import functools
from flask import (
        Blueprint, 
        flash, 
        g, 
        redirect, 
        render_template, 
        request, 
        session,
        url_for,
        current_app)
from werkzeug.security import check_password_hash, generate_password_hash
from quizzer.db import get_db


########## BLUEPRINTS AND VIEWS ##########

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                        "INSERT INTO user (username, email, first_name, last_name, password) VALUES (?, ?, ?, ?, ?)",
                        (username, email, first_name, last_name, generate_password_hash(password)),
                        )
                db.commit()
                current_app.logger.info(f"User '{username}' registered successfuly")
            except db.IntegrityError:
                error = f"User {username} or email {email} is already registered."
            else:
                return redirect(url_for("auth.login"))
                
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Wrong password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            # logging successful users
            current_app.logger.info(f"{user['username']} logged in successfully")
            flash("You are now logged in.")
            return redirect(url_for('auth.profile'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
                ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        if g.user['role'] != 'admin':
            return render_template('auth/restricted.html')

        return view(**kwargs)

    return wrapped_view


@bp.route('/profile')
@login_required
def profile():
    db = get_db()
    scores = db.execute(
        'SELECT * FROM quiz_score ' 
        'WHERE taker_id = ? ORDER BY score DESC', 
        (g.user['id'],)
        ).fetchall()
    return render_template('auth/profile.html', scores=scores)

