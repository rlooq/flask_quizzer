from . import quiz
from .qdb import get_qdb
from ..db import get_db
from ..auth import login_required
from flask import render_template, g, request, redirect, session, url_for
from tinydb import Query
from dataclasses import dataclass

# QUESTION CLASS
@dataclass
class Question():
    id: int
    prompt: str
    options: list
    correct: str
    category: str
    attempt: str = None

    def check_answer(self):
        return self.attempt == self.correct



def get_questions(category=None):
    qdb = get_qdb()
    Entry = Query()
    if not category:
        category = "Trivia 1"
    questions = [
        Question(
            id=item.doc_id,
            prompt=item['prompt'],
            options=item['options'],
            correct=item['correct'],
            category=item['category']
            )
        for item in qdb.search(Entry.category==category)
    ]
    return questions

def get_categories():
    qdb = get_qdb()
    categories = {
        item.get('category') for item in qdb.search(
            Query().category.exists()
            )
        }
    return sorted(list(categories))

# VIEW FUNCTIONS
@quiz.route("/quiz_request/<quiz_type>", methods=['GET', 'POST'])
@login_required
def quiz_request(quiz_type):
    if request.method == 'GET':
        categories = [item for item in get_categories() if item.startswith(quiz_type)]
        return render_template('quiz/quiz_request.html', categories=categories)
    elif request.method == 'POST':
        session['category'] = request.form['category']
        return redirect(url_for('quiz.quiz'))


@quiz.route("/quiz/", methods=['GET', 'POST'])
@login_required
def quiz():
    category = session.get('category')
    questions = get_questions(category)
    
    if request.method == 'GET':
        return render_template('quiz/quiz.html', questions=questions, category=category)
    
    elif request.method == 'POST':
        for question, answer in zip(questions, request.form.values()):
            question.attempt = answer
        score = 0
        for question in questions:
            if question.check_answer():
                score +=1
        
        weighed_score = round(score*10/len(questions), 1)
        
        db = get_db()
        db.execute(
                'INSERT INTO quiz_score (taker_id, quiz_taken, score)'
                ' VALUES (?, ?, ?)',
                (g.user['id'], category, weighed_score)
            )
        db.commit()
        session.pop('category', None)    
        return render_template('quiz/quiz_result.html', questions=questions, score=score, category=category)
    
    

    

