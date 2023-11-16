from flask import Blueprint, send_file
from flask import render_template, request, url_for, flash, redirect, abort
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, delete, create_engine
from ddtool import db
from ddtool.models import Appdata, Reinstate, Reins2
from ddtool.modelform import Reinsfrm
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask import current_app
from fpdf import FPDF
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from ddtool.modelform import Upload
import warnings
import pandas as pd
from ddtool.models import User
warnings.filterwarnings(action='ignore')

ALLOWED_EXTENSIONS = set(['xlsx'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


pdf_reader = PdfReader

reinstate = Blueprint('reinstate', __name__, template_folder='templates')


def numOfDays(date1, date2):
    # check which date is greater to avoid days output in -ve number
    if date2 > date1:
        return (date2 - date1).days
    else:
        return (date1 - date2).days


@reinstate.route('/reinstate_adcb/<int:id2>', methods=['GET', 'POST'])
@login_required
def reinstate_adcb(id2):
    pdf_merger = PdfMerger()
    if current_user.bankname != 'ADCB':
        abort(403)
    form = Reinsfrm()
    data2 = Reins2.query.filter(Reins2.id == id2).order_by(Reins2.id.desc()).first()
    current_app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    if form.validate_on_submit():
        images1 = []
        pdf_file1 = []
        for file in request.files.getlist('attachment'):
            filename = secure_filename(file.filename)
            if filename:
                if filename.rsplit('.', 1)[1].lower() in ['jpg', 'png', 'jpeg']:
                    images1.append(filename)
                else:
                    pdf_file1.append(filename)

        data2.doc_path = os.path.join(current_app.config['UPLOADS_FOLDER'],
                                          f"{data2.customer_name}_{data2.bankref}_merged.pdf")
        data2.justification = form.Justification.data
        data2.rejection = form.rejection_reason.data
        data2.date=datetime.now()
        db.session.commit()

        class PDF(FPDF):
            def footer(self):
                self.set_y(-50)
                self.set_x(-50)
                self.image('/home/afzal/PycharmProjects/ecsa/ddtool/static/stamps/82266.png', w=50, h=30)

        pdf = PDF(orientation='P')
        TABLE_DATA = (("Name", data2.customer_name),
                      ("LapsID", data2.bankref),
                      ("Date", str(datetime.date(data2.date))),
                      ("Decline Reason", data2.rejection),
                      ("Business Justification", data2.justification))
        pdf.add_page()
        pdf.set_font("Times", size=16)
        pdf.set_x(60)
        pdf.cell(60, 20, "ITMAM REINSTATE MEMO"
                 )
        pdf.ln(20)
        with pdf.table(col_widths=(20, 50), text_align='CENTER') as table:
            for data_row in TABLE_DATA:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

        for file in request.files.getlist('attachment'):
            filename = secure_filename(file.filename)
            if filename in images1:
                #print("if you are coming here")
                file.save(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
                pdf.add_page()
                pdf.image(file, h=pdf.eph / 1.5, w=pdf.epw / 1.5, x=40, y=30)
                del images1[0]
                if len(images1) == 0:
                    pdf.output(os.path.join(current_app.config['UPLOADS_FOLDER'],
                                            f"{data2.customer_name}_{data2.bankref}.pdf"))
            if len(images1) == 0:
                pdf.output(os.path.join(current_app.config['UPLOADS_FOLDER'],
                                        f"{data2.customer_name}_{data2.bankref}.pdf"))

            if filename in pdf_file1:
                file.save(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))

        def merger() -> object:
            x = os.path.join(current_app.config['UPLOADS_FOLDER'],
                             f"{data2.customer_name}_{data2.bankref}.pdf")
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
                                   f"{data2.customer_name}_{data2.bankref}_merged.pdf"),
                      "wb") as f:
                pdf_merger.write(f)

            return os.path.join(current_app.config['UPLOADS_FOLDER'],
                                f"{data2.customer_name}_{data2.bankref}_merged.pdf")
        merger()
        flash("Submitted Successfully")
        pdf_merger.close()
        return redirect(url_for('reinstate.reinstate_agent'))
    else:
        form.customer_name.data =   data2.customer_name
        form.LapsID.data = data2.bankref
        form.date.data = datetime.date(data2.date)
        form.rejection_reason.data = data2.rejection
        form.Justification.data = data2.justification
    if request.method == 'GET':
        form.customer_name.data = data2.customer_name
        form.LapsID.data = data2.bankref
        form.date.data = datetime.date(data2.date)
        form.rejection_reason.data = data2.rejection
        form.Justification.data = data2.justification
    return render_template('reinstate.html', form=form, id=id2)


@reinstate.route('/reinstate_agent', methods=['GET', 'POST'])
@login_required
def reinstate_agent():
    if current_user.bankname!="ADCB":
        abort(403)
    else:
        #record = db.session.query(Reinstate).join(Appdata).filter(Appdata.agent_id == current_user.hrmsID)
        record = Reins2.query.filter(Reins2.bankcode==current_user.bankcode).all()
    # for r in record:
    # if (r.appdata.bank_status != "Reinstate") and (r.appdata.agent_id != current_user.hrmsID):
    # record.pop()
    return render_template('reinstate_agent.html', record=record, str=str, datetime=datetime, days=numOfDays)


@reinstate.route('/reinstate_home', methods=['GET', 'POST'])
@login_required
def reinstate_home():
    """reinstate2 = db.session.query(Reinstate).join(Appdata).filter(
        and_(Reinstate.doc_path != None, Appdata.bank_status == "Reinstate")).order_by(Reinstate.date.desc()).all()"""
    if current_user.userlevel not in ["4", "5"]:
        abort(403)
    else:
        reinstate2=db.session.query(Reins2).join(User).filter(and_(User.coordinator_hrmsid==current_user.hrmsID, Reins2.justification!=None)).order_by(Reins2.date.desc()).all()    
    return render_template('reinstate_home.html', record=reinstate2, str=str, datetime=datetime, days=numOfDays)


@reinstate.route('/download/<int:id>', methods=['GET', 'POST'])
@login_required
def download(id):
    path = Reins2.query.filter(Reins2.id == id).order_by(Reins2.date.desc()).first().doc_path
    if current_user.userlevel not in ["4", "5"]:
        abort(403)
    elif path and os.path.isfile(path=path):
        return send_file(path, as_attachment=True)
    else:
        flash("No attachments were provided")
        return redirect(url_for('reinstate.reinstate_home'))
    return render_template('reinstate_home.html')


@reinstate.route('/reinstateupload', methods=['GET', 'POST'])
@login_required
def reinstateupload():
    if current_user.userlevel not in ["4", "5"]:
        abort(403)
    form=Upload()
    if form.validate_on_submit():
        stmt=db.session.query(Reins2).join(User).filter(User.coordinator_hrmsid==current_user.hrmsID).all()
        #print(type(stmt))
        #print(len(stmt))
        #print(stmt)
        for row in stmt:
            db.session.delete(row)
            db.session.commit()
        #db.session.delete(stmt)
        #db.session.commit()
        file=form.upload.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
            df = pd.read_excel(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
            df.dropna(how='any', inplace=True)
            df.reset_index(drop=True, inplace=True)
            bnk_code=[]
            for col in df.columns:
                df[col]=df[col].str.strip().str.upper()
            for i, row in df.iterrows():
                renst=Reins2()
                renst.bankcode=df.iloc[i,0]
                renst.bankref=df.iloc[i,1]
                renst.customer_name=df.iloc[i,2]
                renst.company=df.iloc[i,3]
                renst.rejection=df.iloc[i,4]
                usr=User.query.filter(User.bankcode==renst.bankcode).first()
                if usr and usr.coordinator_hrmsid==current_user.hrmsID:
                    renst.user=usr
                    db.session.add(renst)
                    db.session.commit()
                else:
                    bnk_code.append(df.iloc[i,0])    
            flash(f"File uploaded succcessfully {len(bnk_code)} records are not updated because these bankcode {bnk_code} is not of your team")
            return redirect(url_for('utils.success'))
        else:
            flash("Only xlsx files can be uploaded")
    return render_template('upload.html', form=form)        


   