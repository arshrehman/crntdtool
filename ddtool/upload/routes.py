import sqlite3

from flask import Blueprint
from sqlalchemy import and_

from ddtool.models import Appdata, Reinstate
from ddtool.modelform import Upload
from flask import render_template, url_for, flash, redirect, abort
from flask_login import login_required, current_user
from ddtool import db
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd
import os
from flask import current_app
import numpy as np
from fuzzywuzzy import process, fuzz
import warnings

from ddtool.models import User

warnings.filterwarnings(action='ignore')

ALLOWED_EXTENSIONS = set(['xlsx'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

upload=Blueprint('upload', __name__)


@upload.route('/upload_adcb', methods=['GET', 'POST'])
@login_required
def upload_adcb():
    if current_user.userlevel not in ["4", "5"]:
        abort(403)
    form = Upload()
    lst_updated = []
    if form.validate_on_submit():
        file = form.upload.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
            df = pd.read_excel(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
            df.dropna(how='any', inplace=True)
            df.reset_index(drop=True, inplace=True)
            for col in df.columns:
                df[col]=df[col].str.strip().str.upper()
            df['join']=df.iloc[:,0] + "|" + df.iloc[:,1] + "|" +df.iloc[:,2]
            bank_code=tuple(np.unique(df.iloc[:,0].values))
            sqliteConnection = sqlite3.connect('instance/site.db')
            cursor = sqliteConnection.cursor()
            result = cursor.execute(f"SELECT hrmsID from user where bankcode in {bank_code}")
            r2=result.fetchall()
            lst_r2 = []
            for i in r2:
                lst_r2.append(i[0])
            query = f"SELECT appdata.customer_name, appdata.company, appdata.entry_date, appdata.leadid, user.bankcode from appdata inner join user on appdata.agent_id=user.hrmsID WHERE appdata.agent_id in {tuple(lst_r2)};"
            df2=pd.read_sql(query,sqliteConnection)
            cursor.close()
            df2['entry_date']=pd.to_datetime(df2['entry_date'])
            df2 = df2[['entry_date', 'leadid', 'bankcode', 'customer_name', 'company']]
            df2['customer_name'] = df2['customer_name'].str.strip().str.upper()
            df2['company'] = df2['company'].str.strip().str.upper()
            df2['bankcode'] = df2['bankcode'].str.strip()
            df2.sort_values(by=['entry_date'], ascending=False, inplace=True)
            df2['join'] = df2['bankcode'] + "|" + df2['customer_name'] + "|" + df2['company']

            def sml(row1, row2):
                index_array_upload = []
                ratio_array = []
                index_array_of_database = []
                for x in row1:
                    if x in row2:
                        index_array_upload.append(row1.index(x))
                        ratio_array.append(100)
                        index_array_of_database.append(row2.index(x))
                    else:
                        y = process.extractOne(x, row2, scorer=fuzz.token_set_ratio, score_cutoff=80)
                        if y and x[:10] == y[0][:10]:
                            index_array_of_database.append(row2.index(y[0]))
                            index_array_upload.append(row1.index(x))
                            ratio_array.append(y[1])
                return index_array_upload, ratio_array, index_array_of_database

            str2match = df['join'].dropna().tolist()
            stroptions = df2['join'].dropna().tolist()

            index_upload, similarity, index_database = sml(str2match, stroptions)
            df3 = pd.DataFrame()
            df3['index_upload'] = pd.Series(index_upload)
            df3['database_index'] = pd.Series(index_database)
            leadids = []
            for x in df3.iloc[:, 1].values:
                leadids.append(df2.iloc[x, 1])
            df3['leadid'] = pd.Series(leadids)
            for index,row in df3.iterrows():
                appdata=Appdata.query.filter(Appdata.leadid==row['leadid']).order_by(Appdata.id.desc()).first()
                rei=Reinstate.query.filter(Reinstate.appdata_id==appdata.id).order_by(Reinstate.id.desc()).first()
                if rei:
                    rei.rejection=df.iloc[row['index_upload'],5]
                    appdata.bookingdate=datetime.now()
                    appdata.bank_reference=df.iloc[row['index_upload'],3]
                    appdata.bank_status=df.iloc[row['index_upload'],4].capitalize()
                    db.session.commit()
                    lst_updated.append(index)
                elif df.iloc[row['index_upload'],4].strip().upper()=="REINSTATE":
                    reinst_reason=df.iloc[row['index_upload'],5]
                    reinst_app=df.iloc[row['index_upload'],3]
                    reinst=Reinstate(rejection=reinst_reason)
                    appdata.bank_reference=reinst_app
                    appdata.bank_status=df.iloc[row['index_upload'],4].capitalize()
                    appdata.bookingdate=datetime.now()
                    reinst.appdata=appdata
                    db.session.add(reinst)
                    db.session.commit()
                    lst_updated.append(index)
                else:
                    appdata.bank_status=df.iloc[row['index_upload'],4].capitalize()
                    appdata.bookingdate=datetime.now()
                    appdata.bank_reference=df.iloc[row['index_upload'],3]
                    appdata.remarks=df.iloc[row['index_upload'],5]
                    db.session.commit()
                    lst_updated.append(index)

            lst_mis = list(df.index)
            lst_index = list(df3['index_upload'].values)
            lst_final = list(set(lst_mis) - set(lst_index))
            lst_customer=[]
            for i in lst_final:
                lst_customer.append(df.iloc[i,1])
            flash(f"{len(lst_updated)} records are updated successfully and {len(lst_customer)} are not matched. Not matched customer names {lst_customer}")
        else:
            flash("Only xlsx files can be uploaded")
    return render_template('upload.html', form=form)


@upload.route('/upload_bankstatus', methods=['GET', 'POST'])
@login_required
def upload_bankstatus():
        if current_user.userlevel not in ["4","5"]:
            abort(403)
        form = Upload()
        lst_not_updated=[]
        lst_updated=[]
        if form.validate_on_submit():
            file = form.upload.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
                df=pd.read_excel(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
                lst_df = list(df.columns)
                lst_df= [x.strip() for x in lst_df]
                lst_df = [x.lower() for x in lst_df]
                df.columns = lst_df
                ar = df.iloc[:,0].values
                ar2 = df.iloc[:,1].values
                df.iloc[:,2] = pd.to_datetime(df.iloc[:,2]).dt.date
                ar3 = list(df.iloc[:,2])
                ar4 = df.iloc[:,3].values

                if (df.isnull().sum().sum())>0:
                    flash("You uploaded a file which has null values. System will not process it.")
                    return redirect(url_for('upload.upload_bankstatus'))
                else:
                    for i in range(len(ar)):
                        if str(ar2[i]).strip().capitalize() not in ['InProcess','Booked','Declined','Approved',"Not-workable","Pending-with-sales","Wip","Reinstate"]:
                            flash(f"second column must have any one of [InProcess,Booked,Declined,Approved,Not-workable, Pending-with-sales, Wip, Reinstate], {i}th cell in second column has invalid value \'{ar2[i]}\'")
                            return redirect(url_for('upload.upload_bankstatus'))
                        elif ar2[i]=="Reinstate":
                            row = Appdata.query.filter_by(leadid=str(ar[i])).order_by(Appdata.id.desc()).first()
                            if row:
                                reins=Reinstate(rejection=ar4[i])
                                row.bank_status=ar2[i]
                                row.bookingdate=ar3[i]
                                reins.appdata=row
                                db.session.add(reins)
                                db.session.commit()
                                lst_updated.append(str(ar[i]))
                            else:
                                lst_not_updated.append(str(ar[i]))
                        else:
                            row = Appdata.query.filter_by(leadid=str(ar[i])).order_by(Appdata.id.desc()).first()
                            if row:
                                lst_updated.append(str(ar[i]))
                                row.bank_status=str(ar2[i]).strip().capitalize()
                                row.bookingdate=(ar3[i])
                                row.remarks=ar4[i]
                                db.session.commit()
                            else:
                                lst_not_updated.append(str(ar[i]))
                    flash(f"{len(lst_updated)} records are updated and {len(lst_not_updated)} records are not matched, not matched leadids are {lst_not_updated}")
                    return redirect(url_for('upload.upload_bankstatus'))
            else:
                flash("Not uploaded, please upload only xlsx file")
                return redirect(url_for('upload.upload_bankstatus'))
        return render_template('upload.html', form=form)


@upload.route('/upload_cpv', methods=['GET', 'POST'])
@login_required
def upload_cpv():
        if current_user.userlevel not in ["4","5"]:
            abort(403)
        form = Upload()
        lst_not_updated=[]
        lst_updated=[]
        if form.validate_on_submit():
            file = form.upload.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
                df=pd.read_excel(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
                lst_df = list(df.columns)
                lst_df= [x.strip() for x in lst_df]
                lst_df = [x.lower() for x in lst_df]
                df.columns = lst_df
                ar = df.iloc[:,0].values
                ar2 = df.iloc[:,1].values

                if (df.isnull().sum().sum())>0:
                    flash("You uploaded a file which has null values. System will not process it.")
                    return redirect(url_for('upload.upload_cpv'))
                else:
                    for i in range(len(ar2)):
                        #ar2[i]=str(ar2[i]).strip().capitalize().replace(" ", "_")
                        #ar2[i]="".join(y.capitalize() for y in ar2[i].split("_"))
                        if str(ar2[i]).strip().capitalize() not in ['Verified','Not-verified','Discrepant']:
                            flash(f"Second column must have any one of [Verified, Not-verified] value, {i}th cell in second column has invalid value \'{ar2[i]}\'")
                            return redirect(url_for('upload.upload_cpv'))
                        else:
                            row = Appdata.query.filter_by(leadid=str(ar[i])).order_by(Appdata.id.desc()).first()
                            if row:
                                lst_updated.append(str(ar[i]))
                                row.cpv=str(ar2[i]).strip().capitalize()
                                db.session.commit()
                            else:
                                lst_not_updated.append(str(ar[i]))
                    flash(f"{len(lst_updated)} records are updated and {len(lst_not_updated)} records are not matched, not matched leadids are {lst_not_updated}")
                    return redirect(url_for('upload.upload_cpv'))
            else:
                flash("Not uploaded, please upload only xlsx file")
                return redirect(url_for('upload.upload_cpv'))
        return render_template('upload_cpv.html', form=form)


@upload.route('/upload_bankref', methods=['GET', 'POST'])
@login_required
def upload_bankref():
        if current_user.userlevel not in ["4","5"]:
            abort(403)
        form = Upload()
        lst_not_updated=[]
        lst_updated=[]
        if form.validate_on_submit():
            file = form.upload.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
                df=pd.read_excel(os.path.join(current_app.config['UPLOADS_FOLDER'], filename))
                lst_df = list(df.columns)
                lst_df= [x.strip() for x in lst_df]
                lst_df = [x.lower() for x in lst_df]
                df.columns = lst_df
                ar = df.iloc[:,0].values
                ar2 = df.iloc[:,1].values

                if (df.isnull().sum().sum())>0:
                    flash("You uploaded a file which has null values. System will not process it.")
                    return redirect(url_for('upload.upload_bankref'))
                else:
                    for i in range(len(ar2)):
                        #ar2[i]=str(ar2[i]).strip().capitalize().replace(" ", "_")
                        #ar2[i]="".join(y.capitalize() for y in ar2[i].split("_"))
                        row = Appdata.query.filter_by(leadid=str(ar[i])).order_by(Appdata.id.desc()).first()
                        if row:
                            lst_updated.append(str(ar[i]))
                            row.bank_reference=str(ar2[i]).strip().capitalize()
                            db.session.commit()
                        else:
                            lst_not_updated.append(str(ar[i]))
                    flash(f"{len(lst_updated)} records are updated and {len(lst_not_updated)} records are not matched, not matched leadids are {lst_not_updated}")
                    return redirect(url_for('upload.upload_bankref'))
            else:
                flash("Not uploaded, please upload only xlsx file")
                return redirect(url_for('upload.upload_bankref'))
        return render_template('upload_bankref.html', form=form)


@upload.route('/dashboard')
@login_required
def dashboard():
    pass
