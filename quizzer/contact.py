from flask import (
    Blueprint, 
    g,
    flash, 
    redirect, 
    render_template, 
    request, 
    url_for
)
from quizzer.auth import admin_required, login_required
from quizzer.db import get_db


########## BLUEPRINTS AND VIEWS ##########

bp = Blueprint('contact', __name__)


@bp.route('/messages')
@admin_required
def messages():
    db = get_db()
    messages = db.execute(
        'SELECT m.id, subject, body, created, author_id, username'
        ' FROM message m JOIN user u ON m.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('contact/messages.html', messages=messages)


@bp.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'GET':
        return render_template('contact/contact.html')
    elif request.method == 'POST':
        subject = request.form['subject']
        body = request.form['body']
        error = None

        if not subject:
            error = 'A subject line is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO message (subject, body, author_id)'
                ' VALUES (?, ?, ?)',
                (subject, body, g.user['id'])
            )
            db.commit()
            flash("Message sent")
            return redirect(url_for('news.index'))


@bp.route('/<int:id>/delete_message', methods=('POST',))
@admin_required
def delete_message(id):
    db = get_db()
    db.execute('DELETE FROM message WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('contact.messages'))
