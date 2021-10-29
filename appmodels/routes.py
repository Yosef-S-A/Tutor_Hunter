#!/usr/bin/python3

import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from appmodels import app, db, bcrypt, mail
from appmodels.forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm, UpdateParentProfileForm
from appmodels.models import User, Tutor, Parent_requests
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message, Mail
from datetime import datetime
import smtplib

@app.route("/")
@app.route("/home")
def home():
    return render_template('/index3.html')

@app.route("/about")
def about():
    return render_template('/about.html', title="About")

@app.route("/tutor_list")
def tutor_list():
    page = request.args.get('page', 1, type=int)
    tutors = Tutor.query.paginate(page=page, per_page=2)
    return render_template('/tutor_list.html', tutors=tutors)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.user_type == 'Parent':
            logout_user()
            form = LoginForm()
            return render_template('signup.html', title='Register', form=form)
        flash('You are already Signedin!', 'danger')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #print(form.user_type.data)
        if form.user_type.data == 'Tutor':
            tutor = Tutor(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, user_type=request.form.get('user_type'), password=hashed_password, rate=0.0, header='empty', bio='empty', placesofresidence='empty', lang='empty',)
            db.session.add(tutor)
            db.session.commit()
            flash('Do NOT forget to update your profile so that you can be listed in available tutors list.', 'success')
        else:
            user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, user_type=request.form.get('user_type'), password=hashed_password)
            db.session.add(user)
            db.session.commit()
        
        flash('Your account has been created! You are now able to login', 'success')
        return redirect(url_for('signin'))
    return render_template('signup.html', title='Register', form=form)



@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
           
            if current_user.user_type == 'Tutor' and not(next_page):
               print(current_user.id)
               tutor = Tutor.query.get_or_404(current_user.id)
               return render_template('tutor_home.html', title='profile', tutor=tutor)
            return redirect(next_page) if next_page else redirect(url_for('tutor_list'))
           
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('signin.html', title='Signin', form=form)

@app.route("/signout")
def signout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(6)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/edityourinfo", methods=['GET', 'POST'])
@login_required
def edityourinfo():
    form = UpdateParentProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('edityourinfo'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    return render_template('edityourinfo.html', title='EditInfo', form=form)

@app.route("/editprofile", methods=['GET', 'POST'])
@login_required
def editprofile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
           picture_file = save_picture(form.picture.data)
           current_user.image_file = picture_file
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.rate = form.rate.data
        current_user.bio = form.bio.data
        current_user.lang = form.lang.data
        current_user.header = form.header.data
        current_user.placesofresidence = form.placesofresidence.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('editprofile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.rate.data = current_user.rate
        form.bio.data = current_user.bio
        form.lang.data = current_user.lang
        form.header.data = current_user.header
        form.placesofresidence.data = current_user.placesofresidence
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('edit_profile.html', title='EditProfile', image_file=image_file, form=form)

@app.route("/tutor_list/<int:tutor_id>")
@login_required
def tutor_home(tutor_id):
    print('tutorhome')
    if current_user.is_authenticated and current_user.user_type == 'Parent':
        tutor = Tutor.query.get_or_404(tutor_id)
        return render_template('tutor_home.html', title='profile', tutor=tutor)
    return redirect(url_for('home'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('signin'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('signin'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route('/send_request/<recipient>', methods=['GET', 'POST'])
@login_required
def send_request(recipient):
    user = User.query.filter_by(id=recipient).first_or_404()
    if user:
        
        prequest = Parent_requests(t_id=recipient, p_id=current_user.id, date_requested=datetime.utcnow(), status="Pending")
        db.session.add(prequest)
        db.session.commit()
        flash('Your request has been sent.', 'success')
    return redirect(url_for('tutor_list'))

@app.route('/requests')
@login_required
def requests():
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    prequests = current_user.requested
    pr=[]
    for p in prequests:
        pr.append(User.query.filter_by(id=p.p_id).first())
        #print(pr.username)
    return render_template('requests.html', pr = pr)
    

@app.route('/accepted/<recipient>', methods=['GET', 'POST'])
@login_required
def accepted(recipient):
    user = User.query.filter_by(id=recipient).first_or_404()  
    msg = Message('Tutor Accepted', sender='yosefsamuel11@gmail.com', recipients=[user.email])
    msg.body = f'''{current_user.first_name} has accepted your request you can contact him via {current_user.email}.'''
    mail.send(msg)
    txt = f'''Your contact information is sent to {current_user.first_name}!'''
    flash(txt, 'success')
    return redirect(url_for('tutor_list'))

    


















