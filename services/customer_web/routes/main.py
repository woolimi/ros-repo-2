"""Main app routes."""

from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint('main', __name__, url_prefix='/app')


@main_bp.route('/main')
def main_page():
    if 'user_id' not in session:
        return redirect(url_for('auth.index'))
    return render_template('main.html', user_id=session['user_id'])


@main_bp.route('/pose_scan')
def pose_scan():
    if 'user_id' not in session:
        return redirect(url_for('auth.index'))
    return render_template('pose_scan.html')
