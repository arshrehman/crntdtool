from flask import Blueprint, redirect, flash
from ddtool.models import User
from ddtool.modelform import Appdata1, Reinsfrm
from flask import render_template, request, url_for, flash, redirect, abort
from flask_login import login_required, current_user
from ddtool import db
from datetime import datetime
from wtforms.validators import Optional
from flask import jsonify


apidata = Blueprint('apidata',__name__)

@apidata.route('/data', methods=['GET'])
@login_required
def data():
    rslt = User.query.all()
    bnkcd = []
    for r in rslt:
        bnkcd.append(r.bankcode)
    return jsonify(bnkcd)