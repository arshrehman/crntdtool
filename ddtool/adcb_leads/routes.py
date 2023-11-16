from flask import Blueprint
from ddtool.models import Appdata
from ddtool.adcb_leads.forms import Adcbleads
from flask import render_template, request, url_for, flash, redirect, abort
from flask_login import login_required, current_user
from ddtool import db
from datetime import datetime
from wtforms.validators import Optional, ValidationError
from ..models import Adcb
from ddtool.models import User
import re
import os
from werkzeug.utils import secure_filename
from ..modelform import Download
from sqlalchemy import and_, or_, func
import csv
from flask import current_app, send_file
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from fpdf import FPDF

adcb_leads = Blueprint('adcb_leads', __name__, template_folder='templates')


ALLOWED_EXTENSIONS = set(['jpg','png','jpeg','pdf'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@adcb_leads.route('/adcbleads', methods=['GET', 'POST'])
@login_required
def adcbleads():
    form = Adcbleads()
    form.product_name.choices[0]=form.product_name.choices[9]
    if current_user.userlevel not in ["6","7"]:
        abort(403)

    if request.method=='POST':
        ac2=request.form.get('account_check')
        form.account_check.choices.append(ac2)
        x=request.files.getlist('attachment3')
        z=[]
        for i in x:
            z.append(secure_filename(i.filename))
        if len(re.findall(".",z[0]))>=1:
            for y in x:
                if y and allowed_file(y.filename):
                    pass
                else:
                    flash("It must be a jpg, jpeg, png or pdf file")
        else:
            pass

            
    if form.validate_on_submit():
        images1 = []
        pdf_file1 = []
        for file in request.files.getlist('attachment3'):
            filename = secure_filename(file.filename)
            if filename:
                if filename.rsplit('.', 1)[1].lower() in ['jpg', 'png', 'jpeg']:
                    images1.append(filename)
                else:
                    pdf_file1.append(filename)
        print(images1, pdf_file1)
        data=Adcb()
        pdf_merger = PdfMerger()
        class PDF(FPDF):
            def footer(self):
                self.set_y(-50)
                self.set_x(-50)
                self.cell(20,20, "Submitted")

        pdf = PDF(orientation='P')

        TABLE_DATA = (("Name", form.customer_name.data),
                      ("Mobile", form.mobile.data),
                      ("Date", str(datetime.now()))
        )
        pdf.add_page()
        pdf.set_font("Times", size=16)
        pdf.set_x(60)
        pdf.cell(60, 20, "ADCB LEADS ATTACHED DOCS"
                 )
        pdf.ln(20)
        with pdf.table(col_widths=(20, 50), text_align='CENTER') as table:
            for data_row in TABLE_DATA:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
        

        for file in request.files.getlist('attachment3'):
            filename = secure_filename(file.filename)
            if filename in images1:
                file.save(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
                pdf.add_page()
                pdf.image(file, h=pdf.eph / 1.5, w=pdf.epw / 1.5, x=40, y=30)
                del images1[0]
                if len(images1) == 0:
                    pdf.output(os.path.join(current_app.config['UPLOADS_FOLDER'],
                                            f"{form.customer_name.data}_{form.mobile.data}.pdf"))
            if len(images1) == 0:
                pdf.output(os.path.join(current_app.config['UPLOADS_FOLDER'],
                                        f"{form.customer_name.data}_{form.mobile.data}.pdf"))
        
            if filename in pdf_file1:
                file.save(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
                        
        def merger() -> object:
            x = os.path.join(current_app.config['UPLOADS_FOLDER'],
                             f"{form.customer_name.data}_{form.mobile.data}.pdf")
            y = []
            for i in pdf_file1:
                y.append(os.path.join(current_app.config['UPLOADS_FOLDER'], i))

            input1 = open(x, "rb")
            pdf_merger.append(input1)
            for j in range(len(y)):
                j = open(os.path.join(current_app.config['UPLOADS_FOLDER'], y[j]), "rb")
                if len(y) != 0:
                    pdf_merger.append(j)

            with open(os.path.join(current_app.config['UPLOADS_FOLDER'],
                                   f"{form.customer_name.data}_{form.mobile.data}_merged.pdf"),
                      "wb") as f:
                pdf_merger.write(f)

            return os.path.join(current_app.config['UPLOADS_FOLDER'],
                                f"{form.customer_name.data}_{form.mobile.data}_merged.pdf")
        merger()
        pdf_merger.close()

        data.product_name=form.product_name.data
        data.customer_name=form.customer_name.data
        data.mobile=str(form.mobile.data)
        data.gender=form.gender.data
        data.nationality=form.nationality.data
        data.dob=form.dob.data
        data.passport_number=form.passport_number.data
        data.passport_expiry=form.passport_expiry.data
        data.visa_number=form.visa_number.data
        data.visa_expiry_date=form.visa_expiry_date.data
        data.emirates_id=str(form.emirates_id.data)
        data.length_of_residence=str(form.length_of_residence.data)
        data.marital_status=form.marital_status.data
        data.dependent=form.dependent.data
        data.education=form.education.data
        data.mothername=form.mothername.data
        data.company=form.company.data
        data.office_emirates=form.office_emirates.data
        data.company_phone=form.company_phone.data
        data.building=form.building.data
        data.area=form.area.data
        data.landmark=form.landmark.data
        data.designation=form.designation.data
        data.joiningdate=form.joiningdate.data
        data.department=form.department.data
        data.staffid=form.staffid.data
        data.salary=str(form.salary.data)
        data.customer_email=form.customer_email.data
        data.account_check=str(form.account_check.data)
        data.homecountryaddress=form.homecountryaddress.data
        data.city=form.city.data
        data.telephone=str(form.telephone.data)
        data.reference_name=form.reference_name.data
        data.reference_company=form.reference_company.data
        data.reference_mobile=form.reference_mobile.data
        data.building2=str(form.building2.data) + str(form.flat.data)
        data.area2=form.area2.data
        data.landmark2=form.landmark2.data
        data.residence_type=form.residence_type.data
        data.residential_emirates=form.residential_emirates.data
        data.prefered_billing=form.prefered_billing.data
        data.pickupdate=form.pickupdate.data
        data.pickupaddress=form.pickupaddress.data
        data.user_id=current_user.id
        data.entry_date=datetime.now()
        data.attachment=os.path.join(current_app.config['UPLOADS_FOLDER'],
                                f"{form.customer_name.data}_{form.mobile.data}_merged.pdf")
        db.session.add(data)
        db.session.commit()
        
        flash("Submitted suceessfully")
        return(redirect(url_for('adcb_leads.agent')))  
    return render_template('adcb_leads.html', form=form)



@adcb_leads.route('/agent', methods=['GET', 'POST'])
@login_required
def agent():
    if current_user.userlevel!="6":
        abort(403)
    else:
        record=Adcb.query.filter(Adcb.user_id==current_user.id).order_by(Adcb.entry_date.desc()).all()    
    return render_template('agent.html', record=record, str=str, datetime=datetime)
    


@adcb_leads.route('/adcbedit/<int:id>', methods=['GET', 'POST'])
@login_required
def adcbedit(id):
    data = Adcb.query.get_or_404(id)
    form = Adcbleads()
    lst = list(data.__dict__.items())
    dct = dict(lst)
    lst_dsrd = ['product_name','customer_name', 'mobile', 'gender', 'nationality', 'dob', 'passport_number','passport_expiry',
                'visa_number','visa_expiry_date','emirates_id', 'length_of_residence', 'marital_status','dependent',
                'education','mothername','company','office_emirates','company_phone','building','area','landmark','designation',
                'joiningdate','department','staffid','salary','customer_email', 'account_check','homecountryaddress',
                'city', 'telephone','reference_name','reference_company','reference_mobile','building2','area2','landmark2',
                'residence_type','residential_emirates','prefered_billing','pickupdate','pickupaddress'
                ]
    dct_ordered = {k: dct[k] for k in lst_dsrd}
    if current_user.userlevel not in ["6","7"]:
        abort(403)

    if request.method=='POST':
        ac2=request.form.get('account_check')
        form.account_check.choices.append(ac2)
            
    if form.validate_on_submit():
        data.product_name=form.product_name.data
        data.customer_name=form.customer_name.data
        data.mobile=str(form.mobile.data)
        data.gender=form.gender.data
        data.nationality=form.nationality.data
        data.dob=form.dob.data
        data.passport_number=form.passport_number.data
        data.passport_expiry=form.passport_expiry.data
        data.visa_number=form.visa_number.data
        data.visa_expiry_date=form.visa_expiry_date.data
        data.emirates_id=str(form.emirates_id.data)
        data.length_of_residence=str(form.length_of_residence.data)
        data.marital_status=form.marital_status.data
        data.dependent=form.dependent.data
        data.education=form.education.data
        data.mothername=form.mothername.data
        data.company=form.company.data
        data.office_emirates=form.office_emirates.data
        data.company_phone=form.company_phone.data
        data.building=form.building.data
        data.area=form.area.data
        data.landmark=form.landmark.data
        data.designation=form.designation.data
        data.joiningdate=form.joiningdate.data
        data.department=form.department.data
        data.staffid=form.staffid.data
        data.salary=str(form.salary.data)
        data.customer_email=form.customer_email.data
        data.account_check=str(form.account_check.data)
        data.homecountryaddress=form.homecountryaddress.data
        data.city=form.city.data
        data.telephone=str(form.telephone.data)
        data.reference_name=form.reference_name.data
        data.reference_company=form.reference_company.data
        data.reference_mobile=form.reference_mobile.data
        data.building2=str(form.building2.data) + str(form.flat.data)
        data.area2=form.area2.data
        data.landmark2=form.landmark2.data
        data.residence_type=form.residence_type.data
        data.residential_emirates=form.residential_emirates.data
        data.prefered_billing=form.prefered_billing.data
        data.pickupdate=form.pickupdate.data
        data.pickupaddress=form.pickupaddress.data
        db.session.commit()
        flash("Record Updated Successfully")
        if current_user.userlevel=="6":
            return redirect(url_for('adcb_leads.agent'))
        else:
            return redirect(url_for('adcb_leads.admin2'))
    elif request.method == 'GET':
        form_dct = form.data
        dct_ordered_form = {m: form_dct[m] for m in lst_dsrd}
        dct_form = dict(list(zip(dct_ordered_form, dct_ordered.values())))
        for i in dct_form.keys():
            if isinstance(dct_form[i], datetime):
                form[i].data = dct_form[i]
            elif isinstance(dct_form[i], float):
                form[i].data = int(dct_form[i])
            elif (i in ['salary', 'emirates_id', 'length_of_residence', 'reference_mobile', 'telephone']):
                form[i].data=int(dct_form[i].split('.',1)[0])
            elif (i=='account_check') and (dct_form[i]!='No'):
                form[i].data=int(dct_form[i])
            else:
                form[i].data = dct_form[i]
    return render_template('adcb_leads.html', form=form, str=str, datetime=datetime)


@adcb_leads.route('/download2', methods=['GET', 'POST'])
@login_required
def download2():
    if current_user.userlevel != "7":
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
            flash("end date must be bigger than start date")
            return redirect(url_for('adcb_leads.download2'))

        if current_user.userlevel =="7":
            data = Adcb.query.filter(and_(
                func.datetime(Adcb.entry_date)>=str(sd2), func.datetime(Adcb.entry_date)<=str(ed2))).all()
        lst_dsrd = ['product_name','customer_name', 'mobile', 'gender', 'nationality', 'dob', 'passport_number','passport_expiry',
                'visa_number','visa_expiry_date','emirates_id', 'length_of_residence', 'marital_status','dependent',
                'education','mothername','company','office_emirates','company_phone','building','area','landmark','designation',
                'joiningdate','department','staffid','salary','customer_email', 'account_check','homecountryaddress',
                'city', 'telephone','reference_name','reference_company','reference_mobile','building2','area2','landmark2',
                'residence_type','residential_emirates','prefered_billing','pickupdate','pickupaddress','agent_name'
                ]
        

        
        with open(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), 'w',encoding='UTF8', newline='') as csvfile:
            csvwriter=csv.writer(csvfile,delimiter=",")
            csvwriter.writerow(lst_dsrd)
            for p in data:
                agent_name= User.query.filter(User.id==p.user_id).first().agent_name
                csvwriter.writerow([p.product_name, str(p.customer_name).upper(),p.mobile,p.gender,p.nationality,p.dob,p.passport_number,p.passport_expiry
                                        ,p.visa_number, p.visa_expiry_date, p.emirates_id, p.length_of_residence,p.marital_status,p.dependent,
                                        str(p.education).upper(),p.mothername,p.company,p.office_emirates,p.company_phone,p.building,p.area,p.landmark,p.designation,
                                        p.joiningdate,p.department,p.staffid,p.salary,p.customer_email,p.account_check,p.homecountryaddress,
                                        p.city,p.telephone, p.reference_name,p.reference_company, p.reference_mobile,p.building2, p.area2,
                                        p.landmark2,p.residence_type,p.residential_emirates,p.prefered_billing, p.pickupdate,p.pickupaddress,agent_name])
        return send_file(os.path.join(current_app.config['UPLOADS_FOLDER'], f'{current_user.username}.csv'), mimetype='text/csv', as_attachment=True)
    return render_template('download.html', form=form)


@adcb_leads.route('/admin2', methods=['GET', 'POST'])
@login_required
def admin2():
    if current_user.userlevel!="7":
        abort(403)
    else:
        record=Adcb.query.order_by(Adcb.id.desc()).all()    
    return render_template('agent.html', record=record, str=str, datetime=datetime, user=User)

@adcb_leads.route('/download3/<int:id>', methods=['GET', 'POST'])
@login_required
def download3(id):
    path = Adcb.query.filter(Adcb.id == id).order_by(Adcb.id.desc()).first().attachment
    if current_user.userlevel != "7":
        abort(403)
    elif path and os.path.isfile(path=path):
        return send_file(path, as_attachment=True)
    else:
        flash("No attachment were provided")
        return redirect(url_for('adcb_leads.admin2'))
    return render_template('agent.html')    
    
