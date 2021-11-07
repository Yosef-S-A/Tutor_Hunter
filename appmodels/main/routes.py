from flask import redirect, render_template, request, url_for, Blueprint
from flask_login import current_user, login_required
from appmodels import db
from appmodels.models import Tutor

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('/index3.html')

@main.route("/about")
def about():
    return render_template('/about.html', title="About")

@main.route("/tutor_list")
def tutor_list():
    page = request.args.get('page', 1, type=int)
    tutors = Tutor.query.paginate(page=page, per_page=3)
    return render_template('/tutor_list.html', tutors=tutors)
    
@main.route("/tutor_profile/<int:tutor_id>")
@login_required
def tutor_profile(tutor_id):
    print('tutorhome')
    if current_user.is_authenticated and current_user.user_type == 'Tutor':
        tutor = Tutor.query.get_or_404(tutor_id)
        return render_template('tutor_home.html', title='profile', tutor=tutor)
    return redirect(url_for('main.home'))

@main.route("/tutor_list/<int:tutor_id>")
@login_required
def tutor_home(tutor_id):
    print('tutorhome')
    if current_user.is_authenticated and current_user.user_type == 'Parent':
        tutor = Tutor.query.get_or_404(tutor_id)
        return render_template('tutor_home.html', title='profile', tutor=tutor)
    return redirect(url_for('main.home'))
