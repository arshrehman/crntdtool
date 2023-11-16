from flask import Blueprint
from ddtool.models import Appdata
from ddtool.modelform import Appdata1
from flask import render_template, request, url_for, flash, redirect, abort
from flask_login import login_required, current_user
from ddtool import db
from datetime import datetime
from wtforms.validators import Optional

enbd = Blueprint('enbd', __name__, template_folder='templates')

# insert data to mysql database via html forms
@enbd.route('/insert', methods=['GET', 'POST'])
@login_required
def insert():
    form = Appdata1()
    form.cpv.choices=['Verified', 'Not-verified']
    if request.method=="POST":
        aecb2=request.form.get('aecb')
        form.aecb.choices.append(aecb2)

    if current_user.userlevel=="1":
        form.bank_status.choices=['InProcess']
    else:
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']

    if (current_user.bankname not in ["ENBD"]) and (current_user.userlevel !="5"):
        abort(403)

    if (current_user.bankname=="ENBD") or (current_user.userlevel=="5"):
        form.product_name.choices=["TITANIUM MASTERCARD","GO 4 IT GOLD VISA CARD","GO 4 IT PLATINUM VISA CARD",
                                   "VISA FLEXI VISA CARD","DNATA PLATINUM MASTERCARD","DNATA WORLD MASTERCARD",
                                   "BUSINESS MASTERCARD","BUSINESS REWARDS SIGNATURE VISA CARD","MANCHESTER UNITED MASTERCARD",
                                   "LULU TITANIUM MASTERCARD","LULU PLATINUM MASTERCARD","U BY EMAAR FAMILY VISA CARD",
                                   "U BY EMAAR SIGNATURE VISA CARD","U BY EMAAR INFINITE VISA CARD","SKYWARDS SIGNATURE VISA CARD",
                                   "SKYWARDS INFINITE VISA CARD","GENERIC INFINITE VISA CARD","MARRIOTT BONVOY WORLD",
                                   "ETHIHAD GUEST VISA INSPIRE","ETHIHAD GUEST VISA ELEVATE","PLATINUM VISA CARD","DUO CREDIT CARD"]
        form.application_type.choices=['PHYSICAL','TAB-StandAlone','Tab-Bundle']
    aecb1=request.args.get('aecb')
    if form.validate_on_submit():
        appdata = Appdata()

        if (current_user.bankname=="ENBD") or (current_user.userlevel=="5"):
            appdata.leadid = "719" + str(form.mobile.data[-6:]) + "EN23"

        # customer details
        appdata.entry_date=datetime.now()
        appdata.customer_name = form.customer_name.data
        appdata.mobile = form.mobile.data
        appdata.customer_email = form.customer_email.data
        appdata.gender = form.gender.data
        appdata.nationality = form.nationality.data
        appdata.salary = form.salary.data
        appdata.company = form.company.data
        appdata.designation = form.designation.data
        appdata.ale_status = form.ale_status.data
        appdata.office_emirates = form.office_emirates.data
        appdata.length_of_residence = str(form.length_of_residence.data)
        appdata.length_of_service = str(form.length_of_service.data)
        appdata.dob = form.dob.data

        # customer's documents details
        appdata.emirates_id = form.emirates_id.data
        appdata.EID_expiry_date = form.EID_expiry_date.data
        appdata.passport_number = form.passport_number.data
        appdata.passport_expiry = form.passport_expiry.data
        appdata.visa_expiry_date = form.visa_expiry_date.data
        appdata.cheque_number = form.cheque_number.data
        appdata.cheque_bank = form.cheque_bank.data
        appdata.iban = form.iban.data
        appdata.submissiondate=form.submissiondate.data
        appdata.bookingdate=form.bookingdate.data
        appdata.bankingwith=form.bankingwith.data


        # Agent specific details
        appdata.agent_id = current_user.hrmsID
        appdata.agent_name = current_user.agent_name
        appdata.agent_level = current_user.userlevel
        appdata.bank_name = current_user.bankname
        appdata.tlhrmsid = current_user.tlhrmsid
        appdata.mngrhrmsid=current_user.mngrhrmsid
        appdata.crdntr_hrmsid=current_user.coordinator_hrmsid
        appdata.agent_location = current_user.location



        # Bank Specific details
        appdata.product_type = form.product_type.data
        appdata.product_name = form.product_name.data
        appdata.bank_reference = form.bank_reference.data
        appdata.bank_status = form.bank_status.data
        appdata.application_type=form.application_type.data
        appdata.supplementary_card=form.supplementary_card.data
        appdata.remarks=form.remarks.data
        appdata.cpv=form.cpv.data
        appdata.aecb=form.aecb.data




        # commiting to the database
        db.session.add(appdata)
        db.session.commit()
        flash("Record Inserted Successfully")
        if current_user.userlevel=="1":
            return redirect(url_for('utils.aecb'))
        else:
            return redirect(url_for('utils.success'))

    return render_template('insert.html', form=form)


# update customer record
@enbd.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    data = Appdata.query.get_or_404(id)
    form = Appdata1()
    lst = list(data.__dict__.items())
    dct = dict(lst)
    form.mobile.validators=[Optional()]
    form.nationality.choices[0] = data.nationality
    form.ale_status.choices[0]=data.ale_status

    if current_user.userlevel in ["4","5"]:
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']
        form.cpv.choices=['Verified','Not-verified', 'Discrepant']
        if data.cpv in ['Verified','Not-verified','Discrepant']:
            form.cpv.choices[0]=data.cpv
        else:
            form.cpv.choices.insert(0,data.cpv)

        form.bank_status.choices[0]=data.bank_status

    if current_user.userlevel=="1":
        form.bank_status.choices=[data.bank_status]
        form.cpv.choices=[data.cpv]
    if (current_user.bankname not in ["ENBD"]) and (current_user.userlevel !="5"):
        abort(403)


    if (current_user.userlevel=="4") or (current_user.userlevel=="5"):
        form.product_name.choices = ["TITANIUM MASTERCARD", "GO 4 IT GOLD VISA CARD", "GO 4 IT PLATINUM VISA CARD",
                                     "VISA FLEXI VISA CARD", "DNATA PLATINUM MASTERCARD", "DNATA WORLD MASTERCARD",
                                     "BUSINESS MASTERCARD", "BUSINESS REWARDS SIGNATURE VISA CARD",
                                     "MANCHESTER UNITED MASTERCARD",
                                     "LULU TITANIUM MASTERCARD", "LULU PLATINUM MASTERCARD",
                                     "U BY EMAAR FAMILY VISA CARD",
                                     "U BY EMAAR SIGNATURE VISA CARD", "U BY EMAAR INFINITE VISA CARD",
                                     "SKYWARDS SIGNATURE VISA CARD",
                                     "SKYWARDS INFINITE VISA CARD", "GENERIC INFINITE VISA CARD",
                                     "MARRIOTT BONVOY WORLD",
                                     "ETHIHAD GUEST VISA INSPIRE", "ETHIHAD GUEST VISA ELEVATE", "PLATINUM VISA CARD"]
        form.application_type.choices = ['PHYSICAL', 'TAB-StandAlone', 'Tab-Bundle']
        form.product_name.choices[0]=data.product_name
        form.application_type.choices[0]=data.application_type
    else:
        form.product_name.choices=[data.product_name]
        form.application_type.choices=[data.application_type]


    # dct.pop("entry_date")
    lst_dsrd = ['customer_name', 'mobile', 'customer_email', 'gender', 'nationality', 'salary', 'company','designation',
                  'ale_status', 'office_emirates', 'length_of_residence', 'length_of_service',
                'dob', 'emirates_id', 'EID_expiry_date','passport_number', 'passport_expiry','cheque_number', 'cheque_bank','iban',
                'visa_expiry_date', 'product_type', 'product_name', 'bank_reference', 'bank_status','bankingwith','submissiondate','bookingdate',
                'application_type', 'supplementary_card', 'remarks', 'cpv']
    dct_ordered = {k: dct[k] for k in lst_dsrd}
    if form.validate_on_submit():
        data.customer_name = form.customer_name.data
        data.customer_email = form.customer_email.data
        data.gender = form.gender.data
        data.nationality = form.nationality.data
        data.salary = form.salary.data
        data.company = form.company.data
        data.designation = form.designation.data
        data.ale_status = form.ale_status.data
        data.office_emirates = form.office_emirates.data
        data.length_of_residence = str(form.length_of_residence.data)
        data.length_of_service = str(form.length_of_service.data)
        data.dob = form.dob.data




        data.emirates_id = form.emirates_id.data
        data.EID_expiry_date = form.EID_expiry_date.data
        data.passport_number = form.passport_number.data
        data.passport_expiry = form.passport_expiry.data
        data.cheque_number = form.cheque_number.data
        data.cheque_bank = form.cheque_bank.data
        data.bankingwith = form.bankingwith.data
        data.iban = form.iban.data

        data.visa_expiry_date = form.visa_expiry_date.data
        data.product_type = form.product_type.data
        data.product_name = form.product_name.data
        data.bank_reference = form.bank_reference.data
        data.bank_status = form.bank_status.data

        data.application_type=form.application_type.data
        data.submissiondate=form.submissiondate.data
        data.bookingdate=form.bookingdate.data
        data.supplementary_card=form.supplementary_card.data
        data.remarks=form.remarks.data
        data.cpv=form.cpv.data


        # for i in lst_dsrd:
        # data.i=form.i.data
        db.session.commit()
        flash("Record Updated Successfully")
        if current_user.userlevel=="1":
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
    return render_template('update.html', form=form, id=id, user=current_user)
