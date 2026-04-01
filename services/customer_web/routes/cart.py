"""Cart route."""

from flask import Blueprint, render_template, session, redirect, url_for

cart_bp = Blueprint('cart', __name__, url_prefix='/app')


@cart_bp.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('auth.index'))
    return render_template('cart.html')
