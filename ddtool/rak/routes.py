from flask import Blueprint
from ddtool.models import Appdata
from ddtool.modelform import Appdata1
from flask import render_template, request, url_for, flash, redirect, abort
from flask_login import login_required, current_user
from ddtool import db
from datetime import datetime
from wtforms.validators import Optional

rak=Blueprint('rak', __name__, template_folder='templates')

@rak.route('/insertrak', methods=['GET', 'POST'])
@login_required
def insertrak():
    form1 = Appdata1()
    form1.cpv.choices = ['Verified', 'Not-verified']

    if current_user.userlevel == "1":
        form1.bank_status.choices = ['InProcess']
    else:
        form1.bank_status.choices = ['InProcess','Booked','Declined','Dsa-pending','Docs-required']



    if (current_user.bankname == "RAK") or (current_user.userlevel=="5"):
        form1.product_name.choices = ["MASTERCARD WORLD", "HIGH FLYER PLATINUM", "TITANIUM CARD", "RED CARD",
                                      "ISLAMIC WORLD", "ISLAMIC PLATINUM", "ISLAMIC GOLD", "EMIRATES SKYWARDS WORLD ELITE CARD"]

    if (current_user.bankname not in ["RAK"]) and (current_user.userlevel !="5"):
        abort(403)

    form1.office_emirates.validators=[Optional()]
    form1.gender.validators=[Optional()]

    if form1.validate_on_submit():
        appdata = Appdata()

        if (current_user.bankname == "RAK") or (current_user.userlevel=="5"):
            appdata.leadid = "789" + str(form1.mobile.data[-6:]) + "RK23"


        # customer details
        appdata.customer_name = form1.customer_name.data
        appdata.entry_date=datetime.now()
        appdata.mobile = form1.mobile.data
        appdata.customer_email = form1.customer_email.data
        appdata.nationality = form1.nationality.data
        appdata.salary = form1.salary.data
        appdata.company = form1.company.data
        appdata.ale_status = form1.ale_status.data
        appdata.designation=form1.designation.data
        appdata.bankingwith=form1.bankingwith.data




        # customer's documents details
        appdata.emirates_id = form1.emirates_id.data
        appdata.submissiondate = form1.submissiondate.data
        appdata.bookingdate = form1.bookingdate.data


        # Agent specific details
        appdata.agent_id = current_user.hrmsID
        appdata.agent_name = current_user.agent_name
        appdata.bank_name = current_user.bankname
        appdata.tlhrmsid = current_user.tlhrmsid
        appdata.mngrhrmsid = current_user.mngrhrmsid
        appdata.crdntr_hrmsid = current_user.coordinator_hrmsid
        appdata.agent_location=current_user.location

        # Bank Specific details
        appdata.product_type=form1.product_type.data
        appdata.product_name = form1.product_name.data
        appdata.bank_reference = form1.bank_reference.data
        appdata.bank_status = form1.bank_status.data
        appdata.remarks = form1.remarks.data
        appdata.cpv = form1.cpv.data


        # commiting to the database
        db.session.add(appdata)
        db.session.commit()
        flash("Record Inserted Successfully")
        if current_user.userlevel == "1":
            return redirect(url_for('utils.aecb'))
        else:
            return redirect(url_for('utils.success'))

    return render_template('insertrak.html', form=form1)


@rak.route('/updaterak/<int:id>', methods=['GET', 'POST'])
@login_required
def updaterak(id):
    data = Appdata.query.get_or_404(id)
    form = Appdata1()
    lst = list(data.__dict__.items())
    dct = dict(lst)
    form.mobile.validators=[Optional()]
    usr = current_user
    form.nationality.choices[0] = data.nationality
    form.ale_status.choices[0]=data.ale_status
    form.gender.validators=[Optional()]
    form.office_emirates.validators=[Optional()]
    form.mobile.validators=[Optional()]

    if current_user.userlevel in ["4","5"]:
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']
        form.cpv.choices=['Verified','Not-verified']
        if data.cpv in ['Verified','Not-verified']:
            form.cpv.choices[0]=data.cpv
        else:
            form.cpv.choices.insert(0,data.cpv)

        form.bank_status.choices[0]=data.bank_status

    if current_user.userlevel=="1":
        form.bank_status.choices=[data.bank_status]
        form.cpv.choices=[data.cpv]
    if (current_user.bankname not in ["RAK"]) and (current_user.userlevel !="5"):
        abort(403)


    if (current_user.userlevel=="4") or (current_user.userlevel=="5"):
        form.product_name.choices = ["MASTERCARD WORLD", "HIGH FLYER PLATINUM", "TITANIUM CARD", "RED CARD",
                                      "ISLAMIC WORLD", "ISLAMIC PLATINUM", "ISLAMIC GOLD", "EMIRATES SKYWARDS WORLD ELITE CARD"]
        form.product_name.choices[0]=data.product_name
    else:
        form.product_name.choices=[data.product_name]


    # dct.pop("entry_date")
    lst_dsrd = ['customer_name', 'customer_email', 'nationality', 'salary', 'company','designation',
                  'ale_status', 'emirates_id', 'passport_number', 'bankingwith', 'product_type', 'product_name', 'bank_reference', 'bank_status',
                 'submissiondate','bookingdate', 'supplementary_card','iban','remarks', 'cpv']
    dct_ordered = {k: dct[k] for k in lst_dsrd}
    if form.validate_on_submit():
        data.customer_name = form.customer_name.data
        data.customer_email = form.customer_email.data
        data.nationality = form.nationality.data
        data.salary = form.salary.data
        data.company = form.company.data
        data.designation = form.designation.data
        data.ale_status = form.ale_status.data

        data.emirates_id = form.emirates_id.data
        data.passport_number = form.passport_number.data
        data.bankingwith = form.bankingwith.data

        data.product_type = form.product_type.data
        data.product_name = form.product_name.data
        data.bank_reference = form.bank_reference.data
        data.bank_status = form.bank_status.data

        data.submissiondate=form.submissiondate.data
        data.bookingdate=form.bookingdate.data
        data.supplementary_card=form.supplementary_card.data
        data.iban=form.iban.data
        data.remarks=form.remarks.data
        data.cpv=form.cpv.data


        # for i in lst_dsrd:
        # data.i=form.i.data
        db.session.commit()
        flash("Record Updated Successfully")
        if usr.userlevel=="1":
            return redirect(url_for('utils.aecb'))
        else:
            return redirect(url_for('utils.success'))
    elif request.method == 'GET':
        form_dct = form.data
        #print(form.data)
        dct_ordered_form = {m: form_dct[m] for m in lst_dsrd}
        dct_form = dict(list(zip(dct_ordered_form, dct_ordered.values())))
        for i in dct_form.keys():
            if isinstance(dct_form[i], datetime):
                form[i].data = dct_form[i]
            elif isinstance(dct_form[i], float):
                form[i].data = int(dct_form[i])
            else:
                form[i].data = dct_form[i]
    return render_template('insertrak.html', form=form, id=id, user=usr)
