"""Auth routes — login page and login POST."""

from flask import Blueprint, render_template, request, session, redirect, url_for

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    user_id = request.form.get('user_id', '').strip()
    password = request.form.get('password', '').strip()
    if not user_id or not password:
        return render_template('login.html', error='아이디와 비밀번호를 입력하세요.')
    session['user_id'] = user_id
    return redirect(url_for('main.main_page'))
