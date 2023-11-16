import os
from flask import Blueprint, current_app
from ddtool.models import Appdata
from ddtool.models import User
from ddtool.modelform import Download
from flask import render_template, request, send_file, abort
from flask_login import login_required, current_user
from datetime import datetime,timedelta
from sqlalchemy import and_, func, join, select
import csv
import re
from wtforms.validators import ValidationError
from ddtool import db

utils=Blueprint('utils',__name__, template_folder='templates')


def numOfDays(date1, date2):
    # check which date is greater to avoid days output in -ve number
    if date2 > date1:
        return (date2 - date1).days
    else:
        return (date1 - date2).days

@utils.route('/success')
@login_required
def success():
    filter_after = datetime.today() - timedelta(days = 150)
    q = request.args.get('q')   
    if current_user.userlevel not in ["2","3", "4", "5"]:
        abort(403)
    elif current_user.userlevel =="2":
        if q:
            all_data = Appdata.query.filter(Appdata.customer_email.contains(q)).all()
        else:
            all_data = Appdata.query.filter(and_(Appdata.entry_date==filter_after, Appdata.tlhrmsid==current_user.hrmsID)).all()
    elif current_user.userlevel=="3":
        if q:
            all_data = Appdata.query.filter(Appdata.customer_email.contains(q)).all()
        else:
            all_data = Appdata.query.filter(and_(Appdata.entry_date == filter_after,
                                             Appdata.mngrhrmsid == current_user.hrmsID)).order_by(Appdata.id.desc()).all()
    elif current_user.userlevel=="4":
        if q:
            all_data = Appdata.query.filter(Appdata.customer_email.contains(q)).all()
        else:
            #all_data = Appdata.query.filter(and_(Appdata.entry_date>=filter_after,
            #Appdata.crdntr_hrmsid == current_user.hrmsID)).join(User, User.hrmsID==Appdata.agent_id).order_by(Appdata.id.desc()).all()
            all_data2 = db.session.query(Appdata.id, Appdata.customer_name, Appdata.customer_email, Appdata.mobile,
                               Appdata.entry_date, Appdata.bank_status, Appdata.leadid, User.agent_name, User.hrmsID).join(User, and_(Appdata.agent_id==User.hrmsID,
                                                                                                 Appdata.crdntr_hrmsid==current_user.hrmsID,
                                                                                                 Appdata.entry_date>=filter_after)).all()
    else:
        if q:
            all_data = Appdata.query.filter(Appdata.customer_email.contains(q)).all()
        else:
            all_data = Appdata.query.order_by(Appdata.id.desc()).all()

    return render_template('success2.html', datetime=datetime, str=str, record2=all_data2)


@utils.route('/aecb', methods=['GET', 'POST'])
@login_required
def aecb():
    filter_after = datetime.today() - timedelta(days = 60)
    q = request.args.get('q')
    if q:
        aecb_all = Appdata.query.filter(Appdata.customer_name.contains(q)).order_by(Appdata.id.desc()).all()
    else:
        aecb_all = Appdata.query.filter(and_(Appdata.agent_id == current_user.hrmsID,Appdata.entry_date>=filter_after)).order_by(Appdata.id.desc()).all()
    return render_template('aecb.html', record=aecb_all, id=id, datetime=datetime, str=str)



@utils.route('/download', methods=['GET', 'POST'])
@login_required
def download():
    global data
    if current_user.userlevel not in ["4","5"]:
        abort(403)
    form = Download(request.form)
    if form.validate_on_submit():
        sd1 = form.start.data
        ed1 = form.end.data
        st = form.stime.data
        et = form.etime.data
        sd2 = datetime.combine(sd1,st)
        ed2 = datetime.combine(ed1,et)

        #print(sd2,ed2)
        #print(str(sd2), str(ed2))

        if ed2 < sd2:
            raise ValidationError("End date must not be less than Start date")
        
        if ((current_user.userlevel =="4") and (current_user.bankname=="DEEM")):
            data = db.session.query(Appdata.id, Appdata.leadid, Appdata.entry_date, Appdata.customer_name, Appdata.customer_email,
                                    Appdata.mobile,Appdata.passport_number, User.tlname, Appdata.product_type,
                                    Appdata.product_name, Appdata.contactoffice, Appdata.company, Appdata.ale_status,
                                    Appdata.salary, Appdata.designation, Appdata.joiningdate, Appdata.emirates_id,
                                    Appdata.bankingwith, Appdata.iban, Appdata.bankcode2, Appdata.bank_status, 
                                    User.hrmsID, User.agent_name, Appdata.agent_id, Appdata.cpv, Appdata.bookingdate,
                                    Appdata.remarks).join(User, and_(Appdata.agent_id==User.hrmsID, Appdata.crdntr_hrmsid==current_user.hrmsID,func.date(Appdata.entry_date) >= str(sd2),
                                             func.date(Appdata.entry_date) <= str(ed2))).all()    
        if current_user.userlevel =="5":
            data = db.session.query(Appdata).join(User, and_(Appdata.agent_id==User.hrmsID, Appdata.crdntr_hrmsid==current_user.hrmsID,func.date(Appdata.entry_date) >= str(sd2),
                                             func.date(Appdata.entry_date) <= str(ed2))).all()
        lst_enbd = ['bank_reference', 'leadid', 'entry_date', 'customer_name', 'mobile', 'agent_name', 'agent_hrmsid',
                    'agent_code', 'manager',
                    'nationality', 'product_name', 'bank_name', 'cheque_number', 'office_emirate', 'customer_email',
                    'HRLandline', 'designation',
                    'salary', 'company', 'ale_status', 'emirates_id', 'iban', 'gender', 'dob',
                    'los', 'emiratesid_expiry', 'passport', 'cheque_bank', 'product_type', 'aecb',
                    'bank_status', 'application_type', 'submission_date', 'remarks', 'cpv',
                    'booking_date']

        lst_hilal = ['leadid','entry_date','agent_id','tlhrmsid','mngrhrmsid', 'agent_name', 'customer_name', 'mobile', 'salary',
                   'company','designation','ale_status', 'iban', 'cclimit', 'mothername', 'uaeaddress', 'homecountryaddress',
                     'homecountrynumber','joiningdate', 'ref1name', 'ref2name','ref1mobile', 'ref2mobile',
                     'product_name','bank_reference','bank_status','sent','bookingdate', 'remarks']

        lst_adcb = ['leadid', 'entry_date', 'agent_code', 'customer_name', 'passport', 'salary',
                    'mobile', 'emirates_id', 'company', 'promo', 'nationality', 'ale_status', 'product_name',
                    'application_type', 'agent_name', 'tlname', 'mngrname', 'customer_email', 'bank_reference',
                    'bank_status', 'remarks', 'cpv', 'bookingdate']

        lst_scb = ['leadid', 'entry_date', 'agent_id', 'mngrhrmsid', 'agent_name', 'bank_reference','application_type',
                   'customer_name', 'mobile','company','salary','designation','nationality','ale_status','customer_email',
                    'gender', 'emirates_id', 'salary_account', 'product_type', 'product_name',
                     'bank_status',  'submission_date', 'remarks', 'booking_date']

        lst_cbd = ['leadid', 'entry_date', 'agent_code', 'agent_hrms', 'application_type','customer_name','mobile','product_name',
                   'bank_status', 'remarks', 'nationality', 'company', 'designation', 'salary','customer_email',
                   'salary_account','last6salaries', 'ale_status', 'supplementary_card', 'agent_name', 'bank_reference',
                   'emirates_id', 'cpv', 'booking_date']

        lst_rak = ['leadid', 'entry_date', 'customer_name', 'mobile', 'bank_reference', 'agent_code', 'agent_name',
                   'tlname', 'product_name', 'salary', 'company', 'designation', 'supplementary_card', 'gender',
                   'nationality','customer_email', 'ale_status', 'emirates_id', 'passport', 'bank_name', 'iban', 'bank_status',
                   'remarks','cpv', 'booking_date']
        
        lst_deem = ['entry_date', 'owner', 'leadid', 'customer_name','mobile', 'passport_number', 'team-leader',
                    'product_type', 'product_name', 'contact_office','customer_email','company','ale_status',
                    'salary','designation', 'dateofjoining', 'emirates_id', 'bankingwith','iban', 'appliedsalesagent',
                    'bankcode', 'appliedsalesogid', 'status', 'leadgeneratedname','leadgenogid' ,'cpv', 'booking_date', 'remarks']


        if current_user.bankname=='RAK':
            with open(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter=csv.writer(csvfile,delimiter=",")
                csvwriter.writerow(lst_rak)
                for p in data:
                    bank_code = User.query.filter_by(hrmsID=p.agent_id).first()
                    if bank_code:
                        bankcode=bank_code.bankcode
                        tlname=bank_code.tlname
                    else:
                        bankcode="NA"
                        tlname="NA"
                    csvwriter.writerow([p.leadid, datetime.date(p.entry_date), str(p.customer_name).upper(),p.mobile,p.bank_reference,
                                        bankcode, str(p.agent_name).upper(), tlname, p.product_name,p.salary,str(p.company).upper(),
                                        str(p.designation).upper(),p.supplementary_card,p.gender,p.nationality,str(p.customer_email).upper(),
                                        p.ale_status,p.emirates_id,p.passport_number,p.bankingwith,p.iban,p.bank_status,
                                        p.remarks,p.cpv, p.bookingdate])
            return send_file(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), mimetype='text/csv', as_attachment=True)
                
        if current_user.bankname=='DEEM':
            with open(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter=csv.writer(csvfile,delimiter=",")
                csvwriter.writerow(lst_deem)
                for p in data:
                    eid=p.emirates_id
                    asagentname=User.query.filter(User.bankcode==p.bankcode2).first().agent_name
                    asogid=User.query.filter(User.bankcode==p.bankcode2).first().hrmsID
                    if eid:
                        eid2 = str.join("-",re.findall('(\w{3})(\w{4})(\w{7})(\w{1})', eid)[0])
                    else:
                        eid2=eid
                    csvwriter.writerow([datetime.date(p.entry_date), 'OG_CAPITAL' ,p.leadid, str(p.customer_name).upper(),
                                        p.mobile,p.passport_number,p.tlname,p.product_type, p.product_name,p.contactoffice,
                                        str(p.customer_email).upper(),str(p.company).upper(),p.ale_status,p.salary,p.designation,
                                        p.joiningdate,eid2,p.bankingwith,p.iban,asagentname,p.bankcode2,asogid,p.bank_status,
                                        p.agent_name, p.hrmsID, p.cpv, p.bookingdate, p.remarks])
            return send_file(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), mimetype='text/csv', as_attachment=True)



        if current_user.bankname=='ENBD':
            with open(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter=csv.writer(csvfile,delimiter=",")
                csvwriter.writerow(lst_enbd)
                for p in data:
                    bank_code = User.query.filter_by(hrmsID=p.agent_id).first()
                    if bank_code:
                        bankcode = bank_code.bankcode
                        manager=bank_code.manager
                    else:
                        bankcode="NA"
                        manager="NA"
                    csvwriter.writerow([str(p.bank_reference),p.leadid, datetime.date(p.entry_date),str(p.customer_name).upper(),p.mobile,str(p.agent_name).upper(),p.agent_id, bankcode,
                                        manager,p.nationality,p.product_name,p.bankingwith,p.cheque_number,p.office_emirates,str(p.customer_email).upper(),
                                        p.length_of_residence,str(p.designation).upper(),p.salary,str(p.company).upper(),p.ale_status, str(p.emirates_id),
                                        p.iban,p.gender, p.dob,p.length_of_service, p.EID_expiry_date, p.passport_number,
                                        p.cheque_bank,  p.product_type, p.aecb,p.bank_status, p.application_type,p.submissiondate,p.remarks,p.cpv, p.bookingdate])
            return send_file(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), mimetype='text/csv', as_attachment=True)

        elif current_user.bankname=="ALHILAL":
            with open(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=",")
                csvwriter.writerow(lst_hilal)
                for p in data:
                    csvwriter.writerow(
                        [p.leadid, datetime.date(p.entry_date),p.agent_id, p.tlhrmsid,p.mngrhrmsid,p.agent_name,p.customer_name,
                         p.mobile,p.salary, p.company, p.designation, p.ale_status, p.iban, p.cclimit,p.mothername,p.uaeaddress,
                         p.homecountryaddress,p.homecountrynumber,p.joiningdate,p.ref1name,p.ref2name,p.ref1mobile,p.ref2mobile,
                         p.product_name,p.bank_reference,p.bank_status,p.sent,p.bookingdate,p.remarks])
            return send_file(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), mimetype='text/csv',
                             as_attachment=True)

        elif current_user.bankname=="ADCB":
            with open(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=",")
                csvwriter.writerow(lst_adcb)
                for p in data:
                    eid=p.emirates_id
                    if eid:
                        eid2 = str.join("-",re.findall('(\w{3})(\w{4})(\w{7})(\w{1})', eid)[0])
                    else:
                        eid2=eid

                    bank_code = User.query.filter_by(hrmsID=p.agent_id).first()
                    if bank_code:
                        bankcode = bank_code.bankcode
                        tlname=bank_code.tlname
                        manager=bank_code.manager
                    else:
                        bankcode="NA"
                        tlname="NA"
                        manager="NA"
                    csvwriter.writerow(
                      [p.leadid, datetime.date(p.entry_date), bankcode, str(p.customer_name).upper(),str(p.passport_number).upper(),
                       p.salary, p.mobile, eid2, str(p.company).upper(),str(p.promo).upper(),p.nationality,str(p.ale_status).upper(),
                       str(p.product_name).upper(),str(p.application_type).upper(),str(p.agent_name).upper(),
                       tlname,manager, str(p.customer_email).upper(),str(p.bank_reference).upper(),
                    str(p.bank_status).upper(), str(p.remarks).upper(), p.cpv, p.bookingdate])
            return send_file(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), mimetype='text/csv',
                             as_attachment=True)

        elif current_user.bankname=="SCB":
            with open(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=",")
                csvwriter.writerow(lst_scb)
                for p in data:
                    csvwriter.writerow(
                        [p.leadid, datetime.date(p.entry_date),p.agent_id, p.mngrhrmsid,p.agent_name,p.bank_reference,p.application_type,p.customer_name,p.mobile,p.company,p.salary,p.designation,
                         p.nationality,p.ale_status,p.customer_email, p.gender,
                         p.emirates_id,p.bankingwith,p.product_type, p.product_name,p.bank_status,
                         p.submissiondate,p.remarks, p.bookingdate])
            return send_file(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), mimetype='text/csv',
                             as_attachment=True)

        else:
            lst_admin=list(data[0].__dict__.keys())
            with open(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'),'w',encoding='UTF8',newline='') as csvfile:
                csvwriter=csv.writer(csvfile,delimiter=',')
                csvwriter.writerow(lst_admin[1:])
                for p in data:
                    dct = p.__dict__
                    dct.pop('_sa_instance_state')
                    lst_dct=dct.values()
                    csvwriter.writerow(lst_dct)
            return send_file(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), mimetype='text/csv', as_attachment=True)

    return render_template('download.html', form=form)
