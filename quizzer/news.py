from flask import (
    Blueprint, 
    flash, 
    g, 
    redirect, 
    render_template, 
    request, 
    url_for
)
from werkzeug.exceptions import abort
from quizzer.auth import admin_required
from quizzer.db import get_db


########## BLUEPRINTS AND VIEWS ##########

bp = Blueprint('news', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('news/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@admin_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('news.index'))

    return render_template('news/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@admin_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('news.index'))

    return render_template('news/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@admin_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('news.index'))


@bp.route('/about')
def about():
    return render_template('news/about.html')


@bp.route('/help')
def help():
    return render_template('news/help.html')