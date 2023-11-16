from flask import Blueprint
from ddtool.models import Appdata
from ddtool.modelform import Appdata1
from flask import render_template, request, url_for, flash, redirect, abort
from flask_login import login_required, current_user
from ddtool import db
from datetime import datetime
from wtforms.validators import Optional

adcb = Blueprint('adcb', __name__, template_folder='templates')
@adcb.route('/insertadcb', methods=['GET', 'POST'])
@login_required
def insertadcb():
    form1 = Appdata1()
    usr = current_user
    form1.cpv.choices=['Verified', 'Not-verified']
    if usr.userlevel == "1":
        form1.bank_status.choices = ['InProcess']
    else:
        form1.bank_status.choices = ['InProcess','Booked','Declined','Approved','Not-workable','Pending-with-sales', 'WIP']

    if (current_user.bankname not in ["ADCB"]) and (current_user.userlevel !="5"):
        abort(403)

    if (usr.bankname == "ADCB") or (current_user.userlevel=="5"):
        form1.product_name.choices = ["43-ETIHAD VISA ETIHAD PLATINUM CARD", "365-CASHBACK ISLAMIC CARD",
                                     "201-VISA ISLAMIC COVERED GOLD","200-VISA ISLAMIC COVERED PLATINUM",
                                      "356-VISA 365 CASHBACK CARD","357-VISA VISA ISLAMIC COVERED",
                                     "132-MASTERCARD WORLD TRAVELLER CREDIT CARD", "119-MASTERCARD SIMPLYLIFE CASHBACK CARD",
                                     "9-MASTERCARD TOUCH POINTS PLATINUM CARD", "8-MASTERCARD TOUCH POINTS TITANIUM CARD",
                                      "14-VISA TOUCH POINTS GOLD CARD","16-VISA TOUCH POINTS PLATINUM CARD",
                                     "32-MASTERCARD LULU PLATINUM CARD", "30-MASTERCARD LULU TITANIUM CARD",
                                      "ADCB INFINITE CARD", "ADCB SIGNATURE CARD ", "CASHBACK CARD", '415-MASTERCARD-MASTERCARD Talabat ADCB Credit Card',"BETAQTI CARD"]
        form1.application_type.choices = ['ADCB', 'ISLAMIC', 'SIMPLYLIFE']


    form1.gender.validators=[Optional()]
    form1.office_emirates.validators=[Optional()]

    if form1.validate_on_submit():
        appdata = Appdata()

        if (usr.bankname == "ADCB") or (current_user.userlevel=="5"):
            appdata.leadid = "769" + str(form1.mobile.data[-6:]) + "AD23"

        # customer details
        appdata.customer_name = form1.customer_name.data
        appdata.entry_date=datetime.now()
        appdata.mobile = form1.mobile.data
        appdata.customer_email = form1.customer_email.data
        appdata.nationality = form1.nationality.data
        appdata.salary = form1.salary.data
        appdata.company = form1.company.data
        appdata.ale_status = form1.ale_status.data

        # customer's documents details
        appdata.emirates_id = form1.emirates_id.data
        appdata.passport_number = form1.passport_number.data
        appdata.submissiondate = form1.submissiondate.data
        appdata.bookingdate = form1.bookingdate.data


        # Agent specific details
        appdata.agent_id = usr.hrmsID
        appdata.agent_name = usr.agent_name
        appdata.agent_level = usr.userlevel
        appdata.bank_name = usr.bankname
        appdata.tlhrmsid = usr.tlhrmsid
        appdata.mngrhrmsid = usr.mngrhrmsid
        appdata.crdntr_hrmsid = usr.coordinator_hrmsid
        appdata.agent_location = usr.location

        # Bank Specific details
        appdata.product_name = form1.product_name.data
        appdata.bank_reference = form1.bank_reference.data
        appdata.bank_status = form1.bank_status.data
        appdata.application_type = form1.application_type.data
        appdata.remarks = form1.remarks.data
        appdata.cpv = form1.cpv.data
        appdata.promo = form1.promo.data

        # commiting to the database
        db.session.add(appdata)
        db.session.commit()
        flash("Record Inserted Successfully")
        if usr.userlevel == "1":
            return redirect(url_for('utils.aecb'))
        else:
            return redirect(url_for('utils.success'))

    return render_template('insertadcb.html', form=form1, user=usr)


@adcb.route('/updateadcb/<int:id>', methods=['GET', 'POST'])
@login_required
def updateadcb(id):
    data = Appdata.query.get_or_404(id)
    form = Appdata1()
    lst = list(data.__dict__.items())
    dct = dict(lst)
    form.mobile.validators = [Optional()]
    usr = current_user
    form.nationality.choices[0] = data.nationality
    form.ale_status.choices[0]=data.ale_status

    if current_user.userlevel == "1":
        form.bank_status.choices = [data.bank_status]
        form.cpv.choices=[data.cpv]
    else:
        form.bank_status.choices = ['InProcess','Booked','Declined','Dsa-pending','Docs-required']
        form.bank_status.choices[0]=data.bank_status
        form.cpv.choices=['Verified','Not-verified']
        form.cpv.choices[0]=data.cpv


    if (current_user.bankname not in ["ADCB"]) and (current_user.userlevel !="5"):
        abort(403)

    if (current_user.userlevel == "4") or (current_user.userlevel=="5"):
        form.product_name.choices = ["ADCB INFINITE CARD", "ADCB SIGNATURE CARD ", "CASHBACK CARD", "BETAQTI CARD",
                                      "ADCB ETIHAD GUEST INFINITE CARD", "ADCB ETIHAD GUEST SIGNATURE CARD",
                                      "ADCB ETIHAD GUEST PLATINUM CARD",
                                      "TRAVELLER CREDIT CARD", "TOUCH POINTS INFINITE CARD",
                                      "TOUCH POINTS PLATINUM CARD", "TOUCH POINTS TITANIUM/GOLD CARD",
                                      "LULU PLATINUM CARD", "LULU TITANIUM CARD","415-MASTERCARD-MASTERCARD Talabat ADCB Credit Card"]
        form.application_type.choices = ['CONVENTIONAL', 'ISLAMIC']
        form.application_type.choices[0]=data.application_type
        form.product_name.choices[0]=data.product_name
    else:
        form.product_name.choices=[data.product_name]
        form.application_type.choices=[data.application_type]

    # dct.pop("entry_date")
    lst_dsrd = ['customer_name', 'mobile', 'customer_email', 'nationality', 'salary', 'company',
                'ale_status', 'emirates_id', 'passport_number', 'product_type', 'product_name', 'bank_reference',
                'bank_status','application_type', 'submissiondate', 'bookingdate', 'promo', 'remarks', 'cpv']
    dct_ordered = {k: dct[k] for k in lst_dsrd}

    form.mobile.validators=[Optional()]
    form.gender.validators=[Optional()]
    form.office_emirates.validators=[Optional()]


    if form.validate_on_submit():
        data.customer_name = form.customer_name.data
        data.customer_email = form.customer_email.data
        data.nationality = form.nationality.data
        data.salary = form.salary.data
        data.company = form.company.data
        data.ale_status = form.ale_status.data
        data.emirates_id = form.emirates_id.data
        data.passport_number = form.passport_number.data
        data.product_type = form.product_type.data
        data.product_name = form.product_name.data
        data.bank_reference = form.bank_reference.data
        data.bank_status = form.bank_status.data

        data.application_type = form.application_type.data
        data.submissiondate = form.submissiondate.data
        data.bookingdate = form.bookingdate.data
        data.remarks = form.remarks.data
        data.cpv = form.cpv.data
        data.promo=form.promo.data
        #print("Are you coming here")
        # for i in lst_dsrd:
        # data.i=form.i.data
        db.session.commit()
        flash("Record Updated Successfully")
        if usr.userlevel == "1":
            return redirect(url_for('utils.aecb'))
        else:
            return redirect(url_for('utils.success'))
    elif request.method == 'GET':
        form_dct = form.data
        # print(form.data)
        dct_ordered_form = {m: form_dct[m] for m in lst_dsrd}
        dct_form = dict(list(zip(dct_ordered_form, dct_ordered.values())))
        for i in dct_form.keys():
            if isinstance(dct_form[i], datetime):
                form[i].data = dct_form[i]
            elif isinstance(dct_form[i], float):
                form[i].data = int(dct_form[i])
            else:
                form[i].data = dct_form[i]
    return render_template('updateadcb.html', form=form, id=id, user=usr)
