from flask import Blueprint
from wtforms import StringField
from wtforms.validators import Optional

from .forms import LoginForm, Create
from ddtool.models import User, Appdata
from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, request, url_for, flash, redirect, abort
from ddtool import db
from ddtool import bcrypt
from sqlalchemy import or_

users = Blueprint('users', __name__, template_folder='templates', static_folder='ddtool/static')


@users.route('/')
def index():
    form = LoginForm()
    return render_template('login3.html', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            g = bcrypt.generate_password_hash(user.password)
            if user.userlevel == "2":
                if bcrypt.check_password_hash(g, form.password.data):
                    login_user(user, remember=True)
                    return redirect(url_for('utils.success'))
            if user.userlevel == "1":
                if bcrypt.check_password_hash(g, form.password.data):
                    login_user(user, remember=True)
                    return redirect(url_for('utils.aecb', id=user.hrmsID))
            if user.userlevel in ["2", "3", "4"]:
                if bcrypt.check_password_hash(g, form.password.data):
                    login_user(user, remember=True)
                    return redirect(url_for('utils.success'))
            if user.userlevel == "5":
                if bcrypt.check_password_hash(g, form.password.data):
                    login_user(user, remember=True)
                    return redirect(url_for('utils.success'))
            if user.userlevel == "6":
                if bcrypt.check_password_hash(g, form.password.data):
                    login_user(user, remember=True)
                    return redirect(url_for('adcb_leads.agent'))
            if user.userlevel == "7":
                if bcrypt.check_password_hash(g, form.password.data):
                    login_user(user, remember=True)
                    return redirect(url_for('adcb_leads.admin2'))        
        else:
            flash("Invalid user name or password")
            return redirect(url_for('users.login'))
    return render_template('login3.html', form=form)


@users.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.userlevel not in ["4", "5"]:
        abort(403)
    form = Create()
    if form.validate_on_submit() and current_user.userlevel == "5":
        usr = User()
        usr.username = form.username.data
        usr.password = form.password.data
        usr.hrmsID = form.hrmsid.data
        usr.userlevel = form.usergroup.data
        usr.location = form.location.data
        usr.agent_name = form.name.data
        usr.bankname = form.department.data
        usr.mngrhrmsid = form.mngrhrmsid.data
        usr.manager = form.manager.data
        usr.tlhrmsid = form.tlhrmsid.data
        usr.coordinator_hrmsid = form.crdntrhrmsid.data
        usr.tlname = form.tlname.data
        usr.bankcode = form.bankcode.data

        usr2 = User.query.filter(or_(User.username == usr.username, User.hrmsID == usr.hrmsID)).first()
        if usr2:
            flash("User already exist with this hrmsID or username")
            return render_template('create.html', form=form)
        else:
            db.session.add(usr)
            db.session.commit()
            flash("User created successfully")
            return redirect(url_for('users.all_users'))

    if current_user.userlevel == "4":
        form.crdntrhrmsid.validators = [Optional()]
    if form.validate_on_submit():
        usr = User()
        usr.username = form.username.data
        usr.password = form.password.data
        usr.hrmsID = form.hrmsid.data
        usr.userlevel = "1"
        usr.location = form.location.data
        usr.agent_name = form.name.data
        usr.bankname = current_user.bankname
        usr.mngrhrmsid = form.mngrhrmsid.data
        usr.manager = form.manager.data
        usr.tlhrmsid = form.tlhrmsid.data
        usr.bankcode = form.bankcode.data
        usr.coordinator_hrmsid = current_user.hrmsID
        usr.tlname = form.tlname.data

        usr2 = User.query.filter(or_(User.username == form.username.data, User.hrmsID == form.hrmsid.data)).first()
        if usr2:
            flash("User already exist with this hrmsID or username")
            return render_template('create.html', form=form)
        else:
            db.session.add(usr)
            db.session.commit()
            flash("User created successfully")
            return redirect(url_for('users.all_users'))
    return render_template('create.html', form=form)


@users.route('/all_users', methods=['GET', 'POST'])
@login_required
def all_users():
    if current_user.userlevel not in ["4", "5"]:
        abort(403)
    if current_user.userlevel == "5":
        record = User.query.filter(User.userlevel != "5").all()
    else:
        record = User.query.filter(User.coordinator_hrmsid == current_user.hrmsID)
    return render_template('users.html', record=record)


@users.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    if current_user.userlevel != "5":
        abort(403)
    x = User.query.filter_by(id=id).first()
    db.session.delete(x)
    db.session.commit()
    flash("User deleted successfully")
    return redirect(url_for('users.all_users'))


@users.route('/updateuser/<int:id>', methods=['GET', 'POST'])
@login_required
def updateuser(id):
    if current_user.userlevel not in ["4", "5"]:
        abort(403)

    data2 = User.query.get_or_404(id)
    form = Create()
    form.username.validators = [Optional()]
    form.password.validators = [Optional()]
    form.hrmsid.validators = [Optional()]
    form.name.validators = [Optional()]
    form.crdntrhrmsid.validators = [Optional()]

    if form.validate_on_submit() and current_user.userlevel == "4":
        data2.username = form.username.data
        data2.password = form.password.data
        data2.hrmsID = form.hrmsid.data
        data2.manager = form.manager.data
        data2.location = form.location.data
        data2.agent_name = form.name.data
        data2.mngrhrmsid = form.mngrhrmsid.data
        data2.tlhrmsid = form.tlhrmsid.data
        data2.bankcode = form.bankcode.data
        data2.tlname = form.tlname.data
        print(form.tlname.data)
        print(data2.tlname)

        db.session.commit()
        flash("User updated successfully")
        return redirect(url_for('users.all_users'))
    if form.validate_on_submit() and current_user.userlevel == "5":
        data2.username = form.username.data
        data2.password = form.password.data
        data2.hrmsID = form.hrmsid.data
        data2.bankcode = form.bankcode.data
        data2.userlevel = form.usergroup.data
        data2.manager = form.manager.data
        data2.location = form.location.data
        data2.agent_name = form.name.data
        data2.mngrhrmsid = form.mngrhrmsid.data
        data2.tlhrmsid = form.tlhrmsid.data
        data2.coordinator_hrmsid = form.crdntrhrmsid.data
        data2.tlnamae = form.tlname.data
        data2.bankname = form.department.data

        db.session.commit()
        flash("User updated successfully")
        return redirect(url_for('users.all_users'))

    elif request.method == "GET":
        form.username.data = data2.username
        form.password.data = data2.password
        form.hrmsid.data = data2.hrmsID
        form.department.data = data2.bankname
        form.manager.data = data2.manager
        form.location.data = data2.location
        form.usergroup.data = data2.userlevel
        form.name.data = data2.agent_name
        form.mngrhrmsid.data = data2.mngrhrmsid
        form.crdntrhrmsid.data = data2.coordinator_hrmsid
        form.tlhrmsid.data = data2.tlhrmsid
        form.bankcode.data = data2.bankcode
        form.tlname.data = data2.tlname

    return render_template('updateuser.html', form=form, id=id)


@users.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    if current_user.userlevel not in["4","5"]:
        abort(403)
    x = User.query.filter_by(id=id).first()
    db.session.delete(x)
    db.session.commit()
    flash("Record deleted successfully")
    return redirect(url_for('users.all_users'))


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.index'))
