#!/usr/bin/python3
"""
Routes to render different pages
"""
from flask import redirect, render_template, request, url_for, Blueprint
from flask_login import current_user, login_required
from appmodels import db
from appmodels.models import Tutor

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    """
    A route to render the home page
    """
    return render_template('/index3.html')

@main.route("/about")
def about():
    """
    A route to render the about page
    """
    return render_template('/about.html', title="About")

@main.route("/tutor_list")
def tutor_list():
    """
    A route to render a page to browse tutors from
    """
    page = request.args.get('page', 1, type=int)
    tutors = Tutor.query.paginate(page=page, per_page=3)
    return render_template('/tutor_list.html', tutors=tutors)
    
@main.route("/tutor_profile/<int:tutor_id>")
@login_required
def tutor_profile(tutor_id):
    """
    A route to render the profile page of a tutor
    """
    print('tutorhome')
    if current_user.is_authenticated and current_user.user_type == 'Tutor':
        tutor = Tutor.query.get_or_404(tutor_id)
        return render_template('tutor_home.html', title='profile', tutor=tutor)
    return redirect(url_for('main.home'))

@main.route("/tutor_list/<int:tutor_id>")
@login_required
def tutor_home(tutor_id):
    """
    A route to render the a tutor's personal page
    """
    if current_user.is_authenticated and current_user.user_type == 'Parent':
        tutor = Tutor.query.get_or_404(tutor_id)
        return render_template('tutor_home.html', title='profile', tutor=tutor)
    return redirect(url_for('main.home'))
