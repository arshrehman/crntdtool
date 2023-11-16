from flask import Blueprint
from ddtool.models import Appdata
from ddtool.modelform import Alhilal
from flask import render_template, request, url_for, flash, redirect, abort
from flask_login import login_required, current_user
from ddtool import db
from datetime import datetime
from wtforms.validators import Optional

alhilal=Blueprint('alhilal',__name__, template_folder='templates')

@alhilal.route('/updatehilal/<int:id>', methods=['GET', 'POST'])
@login_required
def updatehilal(id):
    data2 = Appdata.query.get_or_404(id)
    form = Alhilal()
    lst = list(data2.__dict__.items())
    dct = dict(lst)
    form.ale_status.choices[0]=data2.ale_status

    # This is the way to override original form validation of any field.
    form.mobile.validators=[Optional()]
    if current_user.userlevel=="1":
        form.bank_status.choices=[data2.bank_status]

    else:
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']
        form.bank_status.choices[0]=data2.bank_status


    if (current_user.bankname not in ["ALHILAL"]) and (current_user.userlevel !="5"):
        abort(403)

    lst_dsrd = ['customer_name', 'mobile',  'salary', 'company','designation','ale_status', 'iban', 'product_name','bank_reference',
                'bank_status', 'remarks', 'cclimit', 'mothername', 'uaeaddress', 'homecountryaddress', 'homecountrynumber',
                'joiningdate', 'ref1name', 'ref2name','ref1mobile', 'ref2mobile','sent', 'bookingdate']
    dct_ordered = {k: dct[k] for k in lst_dsrd}
    if form.validate_on_submit():
        #print("Print if its reaching here")
        data2.customer_name=form.customer_name.data
        data2.homecountrynumber=form.homecountrynumber.data
        data2.salary=form.salary.data
        data2.bank_reference=form.bank_reference.data
        data2.cclimit=form.cclimit.data
        data2.mothername=form.mothername.data
        data2.company=form.company.data
        data2.designation=form.designation.data
        data2.ale_status=form.ale_status.data
        data2.uaeaddress=form.uaeaddress.data
        data2.homecountryaddress=form.homecountryaddress.data
        data2.iban=form.iban.data
        data2.ref1name=form.ref1name.data
        data2.ref2name=form.ref2name.data
        data2.ref1mobile=form.ref1mobile.data
        data2.ref2mobile=form.ref2mobile.data
        data2.joiningdate=form.joiningdate.data
        data2.remarks=form.remarks.data
        data2.bank_status=form.bank_status.data
        data2.product_name=form.product_name.data
        data2.sent=form.sent.data
        data2.bookingdate = form.bookingdate.data

        db.session.commit()

        flash("Record Updated Successfully")
        if current_user.userlevel == "1":
            return redirect(url_for('utils.aecb'))
        else:
            return redirect(url_for('utils.success'))
    elif request.method == 'GET':
        form_dct = form.data
        # print(form.data)
        dct_ordered_form = {m: form_dct[m] for m in lst_dsrd}
        dct_form = dict(list(zip(dct_ordered_form, dct_ordered.values())))
        #print(dct_form)
        for i in dct_form.keys():
            if isinstance(dct_form[i], datetime):
                form[i].data = dct_form[i]
            elif isinstance(dct_form[i], float):
                form[i].data = int(dct_form[i])
            else:
                form[i].data = dct_form[i]
    return render_template('update2.html', form=form, id=id, user=current_user)


@alhilal.route('/insert2', methods=['GET', 'POST'])
@login_required
def insert2():
    form = Alhilal()
    usr = current_user
    if usr.userlevel=="1":
        form.bank_status.choices=['InProcess']
    else:
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']
    if (current_user.bankname not in ["ALHILAL"]) and (current_user.userlevel !=5):
        abort(403)

    if form.validate_on_submit():
        appdata = Appdata()
        if (usr.bankname == "ALHILAL") or (current_user.userlevel=="5"):
            appdata.leadid = "779" + str(form.mobile.data[-6:]) + "AH23"

        appdata.customer_name=form.customer_name.data
        appdata.entry_date=datetime.now()
        appdata.mobile=form.mobile.data
        appdata.homecountrynumber=form.homecountrynumber.data
        appdata.salary=form.salary.data
        appdata.bank_reference=form.bank_reference.data
        appdata.cclimit=form.cclimit.data
        appdata.mothername=form.mothername.data
        appdata.company=form.company.data
        appdata.designation=form.designation.data
        appdata.ale_status=form.ale_status.data
        appdata.uaeaddress=form.uaeaddress.data
        appdata.homecountryaddress=form.homecountryaddress.data
        appdata.iban=form.iban.data
        appdata.ref1name=form.ref1name.data
        appdata.ref2name=form.ref2name.data
        appdata.ref1mobile=form.ref1mobile.data
        appdata.ref2mobile=form.ref2mobile.data
        appdata.joiningdate=form.joiningdate.data
        appdata.remarks=form.remarks.data
        appdata.sent=form.sent.data
        appdata.bank_status=form.bank_status.data
        appdata.product_name=form.product_name.data

        # Agent specific details
        appdata.agent_id = usr.hrmsID
        appdata.agent_name = usr.agent_name
        appdata.agent_level = usr.userlevel
        appdata.bank_name = usr.bankname
        appdata.tlhrmsid = usr.tlhrmsid
        appdata.mngrhrmsid = usr.mngrhrmsid
        appdata.crdntr_hrmsid = usr.coordinator_hrmsid
        appdata.agent_location = usr.location

        db.session.add(appdata)
        db.session.commit()
        flash("Record Inserted Successfully")
        if usr.userlevel=="1":
            return redirect(url_for('utils.aecb'))
        else:
            return redirect(url_for('utils.success'))

    return render_template('insert2.html', form=form, user=usr)
