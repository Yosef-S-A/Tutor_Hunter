#!/usr/bin/python3
"""
    Flask routes that manage user related functionalities
"""
import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, Blueprint
from appmodels import app, db, bcrypt, mail
from appmodels.users.forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm, UpdateParentProfileForm
from appmodels.users.utility import save_picture, send_reset_email
from appmodels.models import User, Tutor, Parent_requests
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import smtplib
from email.message import EmailMessage
from flask import Flask, session

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    """
    Route that handles new user registration process
    """
    if current_user.is_authenticated:
        if current_user.user_type == 'Parent':
            logout_user()
            form = LoginForm()
            return render_template('signup.html', title='Register', form=form)
        flash('You are already Signedin!', 'danger')
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
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
        return redirect(url_for('users.signin'))
    return render_template('signup.html', title='Register', form=form)


@users.route("/signin", methods=['GET', 'POST'])
def signin():
    """
    Route that handles authenticating and loging them into the system
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
           
            if current_user.user_type == 'Tutor' and not(next_page):
               #print(current_user.id)
               tutor = Tutor.query.get_or_404(current_user.id)
               return redirect(url_for('main.tutor_profile', tutor_id=tutor.id))
            return redirect(next_page) if next_page else redirect(url_for('main.tutor_list'))
           
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('signin.html', title='Signin', form=form)

@users.route("/signout")
def signout():
    """
    route that logsout users from app
    """
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/edityourinfo", methods=['GET', 'POST'])
@login_required
def edityourinfo():
    """
    route that enables registered users who is not tutor
    to edit their profile
    """
    form = UpdateParentProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.edityourinfo'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    return render_template('edityourinfo.html', title='EditInfo', form=form)

@users.route("/editprofile", methods=['GET', 'POST'])
@login_required
def editprofile():
    """
    route that enables registered Tutors to edit their profile
    """
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
        return redirect(url_for('users.editprofile'))
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

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    """
    routes that handles the task of reseting password of registered users
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.signin'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    """
    route that checks whether the user legitmate and it is using
    unexpired token
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.signin'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@users.route('/send_request/<recipient>', methods=['GET', 'POST'])
@login_required
def send_request(recipient):
    """
    route that handles sending request to the respecitve tutor from potential client
    """
    user = User.query.filter_by(id=recipient).first_or_404()
    if user:
        prequest = Parent_requests(t_id=recipient, p_id=current_user.id, date_requested=datetime.utcnow(), status="Pending")
        db.session.add(prequest)
        db.session.commit()
        flash('Your request has been sent.', 'success')
    return redirect(url_for('main.tutor_list'))

@users.route('/requests')
@login_required
def requests():
    """
    route that help the tutors to check if they have incoming requests
    """
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    prequests = current_user.requested
    probj={}
    for p in prequests:
        if not(p.status == 'Accepted'):
            probj[p.id]=User.query.filter_by(id=p.p_id).first()
    if probj:
        return render_template('requests.html', probj = probj)
    flash ('You have no request currently','warning')
    return redirect(url_for('main.tutor_profile', tutor_id=current_user.id))

@users.route('/accepted/<requestid>/parent/<recipient>', methods=['GET', 'POST'])
@login_required
def accepted(requestid, recipient):
    """
    route that handle the process of accepting(the tutor) requests from potential clients
    """
    user = User.query.filter_by(id=recipient).first_or_404()
    msg = EmailMessage()
    message = f'''{current_user.first_name} has accepted your request you can contact him via {current_user.email}.'''
    msg.set_content(message)
    msg['Subject'] = 'Tutor Accepted Your Request'
    msg['From'] = os.environ.get('MAIL_USERNAME')
    msg['To'] = user.email
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))
    server.send_message(msg)
    update_status = Parent_requests.query.filter_by(id=requestid).first()
    update_status.status = 'Accepted'
    db.session.commit()
    txt = f'''Your contact information is sent to {user.first_name}!'''
    flash(txt, 'success')
    return redirect(url_for('users.requests'))

@users.route('/declined/<requestid>', methods=['GET', 'POST'])
@login_required
def declined(requestid):
    """
    route that handle the process(the tutor) of declining requests from potential clients
    """
    delete_this = Parent_requests.query.filter_by(id=requestid).first()
    db.session.delete(delete_this)
    db.session.commit()
    return redirect(url_for('users.requests'))
 
