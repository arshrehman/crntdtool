from flask import Blueprint, redirect, flash, send_file
from ddtool.models import Appdata
from ddtool.modelform import Appdata1, Reinsfrm
from flask import render_template, request, url_for, flash, redirect, abort
from flask_login import login_required, current_user
from ddtool import db
from datetime import datetime
from wtforms.validators import Optional
from werkzeug.utils import secure_filename
import os
from flask import current_app
from functools import reduce
from zipfile import ZipFile, ZIP_DEFLATED



deem=Blueprint('deem', __name__, template_folder='templates')




@deem.route('/insertdeem', methods=['GET', 'POST'])
@login_required
def insertdeem():
    form1 = Appdata1()
    form2 = Reinsfrm()
    form1.cpv.choices = ['Verified', 'Not-verified']

    if current_user.userlevel == "1":
        form1.bank_status.choices = ['InProcess']
    else:
        form1.bank_status.choices = ['InProcess','Booked','Declined','Dsa-pending','Docs-required', 'Rejected', 'End']



    if (current_user.bankname == "DEEM") or (current_user.userlevel=="5"):
        form1.product_name.choices.append(form1.product_name.data)
        form1.application_type.choices = ['DFC','DCC']
        form1.ale_status.choices.clear()
        form1.ale_status.choices=["Please Select","E1", "E2", "E3", "E4"]

    if (current_user.bankname != "DEEM"): 
        abort(403)

    form1.office_emirates.validators=[Optional()]
    form1.gender.validators=[Optional()]

    if form1.validate_on_submit():
        appdata = Appdata()

        if (current_user.bankname == "DEEM") or (current_user.userlevel=="5"):
            appdata.leadid = "789" + str(form1.mobile.data[-6:]) + "DEEM"
        doc_address=[]
        count=0
        for file in request.files.getlist('attachment'):
            count += 1
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))

            filename2= f'{current_user.hrmsID}_{form1.customer_name.data}_eid{count}.{filename.split(".")[1]}'
            os.rename(os.path.join(current_app.config['UPLOADS_FOLDER'], filename),os.path.join(current_app.config['UPLOADS_FOLDER'],filename2))
            doc_address.append(filename2)
            
        res = reduce(lambda x, y: x + '#' + y, map(str, doc_address))

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
        appdata.passport_number=form1.passport_number.data
        appdata.iban=form1.iban.data
        appdata.contactoffice=form1.contactoffice.data
        appdata.joiningdate=form1.joiningdate.data



        # customer's documents details
        appdata.emirates_id = form1.emirates_id.data


        # Agent specific details
        appdata.agent_id = current_user.hrmsID
        appdata.crdntr_hrmsid = current_user.coordinator_hrmsid

        # Bank Specific details
        appdata.product_type=form1.product_type.data
        appdata.product_name = form1.product_name.data
        appdata.remarks = form1.remarks.data
        appdata.docaddress = res
        appdata.bank_status="InProcess"
        if current_user.bankcode!="awaiting":
            appdata.bankcode2 = current_user.bankcode
        else:
            appdata.bankcode2 = form1.bankcode.data    

        # commiting to the database
        db.session.add(appdata)
        db.session.commit()
        flash("Record Inserted Successfully")
        if current_user.userlevel == "1":
            return redirect(url_for('utils.aecb'))
        else:
            return redirect(url_for('utils.success'))

    return render_template('insertcbd.html', form=form1, form2=form2)


@deem.route('/updatedeem/<int:id>', methods=['GET', 'POST'])
@login_required
def updatedeem(id):
    data = Appdata.query.get_or_404(id)
    form = Appdata1()
    lst = list(data.__dict__.items())
    dct = dict(lst)
    usr = current_user
    form.nationality.choices[0] = data.nationality
    form.ale_status.choices[0]=data.ale_status
    form.gender.validators=[Optional()]
    form.office_emirates.validators=[Optional()]
    form.mobile.validators=[Optional()]

    if current_user.userlevel=="4":
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']
        form.cpv.choices=['Verified','Not-verified']
        form.cpv.choices.insert(0, data.cpv)
        form.bank_status.choices[0]=data.bank_status

    if current_user.userlevel=="1":
        form.bank_status.choices=[data.bank_status]
        form.cpv.choices=[data.cpv]
    if (current_user.bankname not in ["DEEM"]) and (current_user.userlevel !="5"):
        abort(403)


    if (current_user.userlevel=="4") or (current_user.userlevel=="5"):
        form.application_type.choices = ['DFC','DCC']
        form.product_name.choices.append(data.product_name)
        form.application_type.choices[0]=data.application_type
    else:
        form.product_name.choices=[data.product_name]
        form.application_type.choices=[data.application_type]


    # dct.pop("entry_date")
    lst_dsrd = ['customer_name', 'customer_email', 'nationality', 'salary', 'company','designation',
                  'ale_status', 'emirates_id', 'passport_number', 'bankingwith', 'product_type', 'product_name', 'bank_reference', 'bank_status',
                'iban','bookingdate','joiningdate', 'remarks', 'cpv', 'contactoffice', 'mobile']
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

        data.bookingdate=form.bookingdate.data
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
        print(dct_form)
        for i in dct_form.keys():
            if isinstance(dct_form[i], datetime):
                form[i].data = dct_form[i]
            elif isinstance(dct_form[i], float):
                form[i].data = int(dct_form[i])
            else:
                form[i].data = dct_form[i]
    return render_template('insertcbd.html', form=form, id=id, user=usr)

@deem.route('/eid/<int:id>', methods=['GET','POST'])
@login_required
def eid(id):
    data = Appdata.query.get_or_404(id)
    #lst_address = [os.path.join(current_app.config['UPLOADS_FOLDER'], x) for x in lst_address]
    if current_user.userlevel not in ["4", "5"]:
        abort(403)

    files_to_zip = str(data.docaddress).split("#")
    zipfile_name= f'{data.agent_id}_{data.customer_name}_eid.zip'
    with ZipFile(os.path.join(current_app.config['UPLOADS_FOLDER'],zipfile_name), 'w', ZIP_DEFLATED) as zip_object:
        for file in files_to_zip:
            file_path = os.path.join(current_app.config['UPLOADS_FOLDER'],file)
            arc_name = os.path.basename(file)
            zip_object.write(file_path, arcname=arc_name)    
        
    if (os.path.join(current_app.config['UPLOADS_FOLDER'], zipfile_name)) and (os.path.isfile(path=os.path.join(current_app.config['UPLOADS_FOLDER'], zipfile_name))):
        return send_file(os.path.join(current_app.config['UPLOADS_FOLDER'],zipfile_name),
                                as_attachment=True)
    else:
        flash("No attachments were provided")
        return redirect(url_for('utils.success'))
    return render_template('success2.html')
