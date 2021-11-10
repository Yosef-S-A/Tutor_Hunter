#!/usr/bin/python3
"""
Utility functions used by routes
"""
import secrets
import os
from PIL import Image
from appmodels import db
from appmodels.models import User
import smtplib
from email.message import EmailMessage

def save_picture(form_picture):
    """
    A function that saves the image uploaded to the system by users
    """
    random_hex = secrets.token_hex(6)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn
    
def send_reset_email(user):
    """
    A function that sends a reset email with time dependent reset link
    """
    token = user.get_reset_token()
    msg = EmailMessage()
    message = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    msg.set_content(message)
    msg['Subject'] = 'Password Reset Request'
    msg['From'] = os.environ.get('MAIL_USERNAME')
    msg['To'] = user.email
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))
    server.send_message(msg)
