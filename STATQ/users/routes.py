from datetime import timedelta  
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app, session
from flask_login import login_user, current_user, logout_user, login_required
from STATQ import db, bcrypt
from STATQ.models import User
from STATQ.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from STATQ.users.utils import send_reset_email
import os

users = Blueprint('users', __name__)

#program = Blueprint('program', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Din konto er nu oprettet! Du kan nu logge ind.', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Logind fejlet. Kontrollér email og kodeord', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        new_path = current_app.root_path+'/static/files/'+current_user.username+'/'
        try:
            os.rename(old_path, new_path)       
        except FileExistsError:
            pass
        flash('Din konto er nu opdateret!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)

@users.route("/nulstil_kodeord", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Instruktioner til nulstilling af kodeord er blevet sendt til din email', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Nulstil kodeord',
                           form=form)


@users.route("/nulstil_kodeord/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Dette er en udløbet eller ugyldig token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Dit kodeord er blevet opdateret! Du kan nu logge ind', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Nulstil kodeord', form=form)
