import os
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import Form, DateTimeField, SubmitField, StringField, PasswordField, BooleanField, IntegerField, \
    SelectField, ValidationError, DateField, FileField,DecimalField,TextAreaField, MultipleFileField
from wtforms.validators import NumberRange, Email, InputRequired, Length, Regexp, DataRequired, Optional
import pandas as pd
from wtforms_components import TimeField
from werkzeug.utils import secure_filename
import re
from ddtool.models import User
#from app import current_user, request

#from application import current_user, request


df = pd.read_csv('/var/www/html/datatoolserver/ddtool/static/files/all_countries.csv')
lst3 = list(df.iloc[:,1])

ALLOWED_EXTENSIONS = set(['jpg','png','jpeg','pdf'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def file_extension():
    def _length(form, field):
        x = field.data
        z=[]
        for a in x:
            z.append(secure_filename(a.filename))
        if len(re.findall(".",z[0]))>=1:
            for y in x:
                if y and allowed_file(y.filename):
                    pass
                else:
                    raise ValidationError("It must be a jpg, jpeg, png or pdf file")
        else:
            pass
    return _length

def length(min=-1, max=-1):
    message = 'Must only have %d digits and must start with 05' % (min)

    def _length(form, field):
        x = field.data
        l = field.data and len(field.data) or 0
        if not x.startswith("05"):
            raise ValidationError("It should start with 05")
        if not x.isdigit():
            raise ValidationError("Mobile number must only have numbers")
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length


def length2(min=-1, max=-1):
    message = 'Must be between %d and %d characters long.' % (min, max)

    def _length(form, field):
        x = field.data
        if not x.isdigit():
            raise ValidationError("Only numbers are allowed")
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length


def length3(min=-1, max=-1):
    message = 'Must be %d characters long.' % (max)

    def _length(form, field):
        x = field.data
        if not x.startswith("784"):
            raise ValidationError("Invalid Emirates ID number")
        if not x.isdigit():
            raise ValidationError("Only numbers are allowed")
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length


def length4(min=-1, max=-1):
    message = 'Must be %d characters long.' % (max)

    def _length(form, field):
        x = field.data
        if not x.startswith("AE"):
            raise ValidationError("Invalid IBAN number")
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length

class Reinsfrm(FlaskForm):
    customer_name = StringField('CustomerName', validators=[Optional(), Length(min=4, max=100)])
    LapsID = StringField('BankReference', validators=[Optional()])
    date = DateField('Date', validators=[Optional()], format="%Y-%m-%d")
    rejection_reason = TextAreaField('RejectionReason', validators=[Optional()])
    Justification = TextAreaField('Justification', validators=[InputRequired(), Length(min=4, max=1000)])
    attachment=MultipleFileField("AttachDocs", validators=[file_extension()])
    submit = SubmitField('Submit')


class Appdata1(FlaskForm):
    customer_name = StringField('CustomerName', validators=[InputRequired(), Length(min=6, max=100)])
    mobile = StringField('Mobile', validators=[DataRequired(), length(10,10)])

    customer_email = StringField('Email', validators=[DataRequired(), Email(message="Invalid Email Address")])
    gender = SelectField('Gender', validators=[InputRequired()],
                         choices=["MALE","FEMALE"])
    nationality = SelectField('Nationality', validators=[InputRequired()], choices=lst3, default=1)
    joiningdate = DateField("DateOfJoining", validators=[InputRequired()])

    salary = DecimalField('Salary', validators=[InputRequired(), NumberRange(min=5000, max=150000)])
    company = StringField('Company', validators=[InputRequired(), Length(min=4, max=100)])
    designation = StringField("Designation", validators=[Optional()])
    ale_status = SelectField("CompanyStatus", validators=[Optional()], choices=["TML", "NTML"])
    office_emirates = SelectField("OfficeEmirates", validators=[InputRequired()], choices=["AbuDhabi", "AlAin","Ajman","Dubai","Fujairah","RasAlKhaima","Sharjah", "UmmAlQuwain"])
    length_of_residence = StringField("ContactOffice", validators=[Optional(),length2(min=1, max=840)])
    length_of_service = StringField("LOS(Months)", validators=[Optional(),length2(min=1, max=840)])
    dob = DateField('DOB', validators=[Optional()])

    emirates_id = StringField('EmiratesID', validators=[Optional(), length3(15, 15)])
    EID_expiry_date = DateField("ExpireOn", validators=[Optional()])
    passport_number = StringField('Passport', validators=[Optional(), Length(min=6, max=20)])
    passport_expiry = DateField("ExpireOn", validators=[Optional()])
    cheque_number = StringField("ChequeNumber", validators=[Optional()])
    cheque_bank = StringField("ChequeBank", validators=[Optional()])
    bankingwith=SelectField("SalaryAccount", validators=[Optional()], choices=["Please Select","ADCB","ADIB", "ENBD", "MASHREQ", "RAK", "CBD", "SCB", "HSBC", "DIB",
                                                                                "FAB","CBI","EIB", "ALMASRAF","BANK OF SHARJAH",
                                                                               "UNITED ARAB BANK","CBI","NBF","NBQ",
                                                                               "SHARJAH ISLAMIC BANK","AL HILAL BANK","AJMAN BANK",
                                                                               "ARAB BANK","BANQUE MISR","BANK OF BARODA","NATIONAL BANK OF BAHRAIN","HBL","CITI",
                                                                               "BANK SEDARAT IRAN","BANK MELLI IRAN","UBL","DEUSTCHE BANK","NBK","BANK OF CHINA",
                                                                               "OTHER"])
    iban = StringField("IBAN", validators=[Optional(), length4(23,23)])
    visa_expiry_date = DateField("VisaExpiryDate", validators=[Optional()])

    product_type = SelectField('Product_type', validators=[InputRequired()],choices=["Please Select","CreditCard", "Loan"])
    product_name = SelectField('CardName', validators=[InputRequired()], choices=[])
    bank_reference = StringField("BankReference", validators=[Optional()])
    bank_status = SelectField("BankStatus", validators=[Optional()], choices=[], default="Inprocess")
    application_type=SelectField("ApplicationType", validators=[Optional()], choices=[])
    submissiondate = DateField("SubmissionDate", validators=[Optional()])
    bookingdate = DateField("BookingDate", validators=[Optional()])
    supplementary_card=SelectField("SupplCard", validators=[Optional()], choices=['NotRequired', 'Required'],default="NotRequired")
    remarks=TextAreaField("Remarks", validators=[Optional()])
    cpv=SelectField("CPV", validators=[Optional()])
    submit = SubmitField('Submit')
    promo = SelectField("Promo", validators=[Optional()], choices=['AECB', 'NCC', 'STC', 'CHLD', 'EMRT'])
    last6salaries=SelectField("Last6Salaries", validators=[Optional()], choices=['YES', 'NO'])
    cbdsource = SelectField("Source", validators=[Optional()], choices=['DIRECT'])
    aecb=SelectField("AECB", validators=[Optional()], choices=['No-Hit', 'Enter AECB score'])
    bankcode=StringField("YourBankCode", validators=[Optional()])
    contactoffice=StringField("OfficeContact", validators=[Optional()])

    
    def validate_bankcode(self, bankcode):
        user_object = User.query.filter_by(bankcode=bankcode.data).first()
        if not user_object:
            raise ValidationError("Invalid, please contact compliance")
        else:
            pass

# Al Hilal Bank specific fields.
class Alhilal(FlaskForm):
    salary = DecimalField('Salary', validators=[InputRequired(), NumberRange(min=5000, max=150000)])
    company = StringField('Company', validators=[InputRequired(), Length(min=4, max=100)])
    designation = StringField("Designation", validators=[Optional()])
    ale_status = SelectField("CompanyStatus", validators=[Optional()], choices=["TML", "NTML"], default="TML")
    customer_name = StringField('CustomerName', validators=[InputRequired(), Length(min=6, max=100)])
    mobile = StringField('Mobile', validators=[DataRequired(),length(10,10)])
    iban = StringField("IBAN", validators=[InputRequired(),length4(23,23)])
    cclimit = StringField("CC-Limit", validators=[InputRequired(), length2(min=1, max=20)])
    mothername = StringField("MotherName", validators=[InputRequired()])
    uaeaddress = StringField("UAEAddress", validators=[InputRequired()])
    homecountryaddress = StringField("HomeCountryAddress", validators=[InputRequired()])
    homecountrynumber = StringField("HomeCountryNumber", validators=[InputRequired(), length2(10,15)])
    joiningdate = DateField("DateOfJoining", validators=[InputRequired()])
    ref1name = StringField("Ref1-Name", validators=[InputRequired()])
    ref2name = StringField("Ref2-Name", validators=[InputRequired()])
    ref1mobile = StringField("Ref1-Mobile", validators=[DataRequired(), length(10,10)])
    ref2mobile = StringField("Ref2-Mobile", validators=[DataRequired(), length(10,10)])
    sent = DateField("Sent", validators=[Optional()])
    remarks = StringField("Remarks", validators=[Optional()])
    bank_reference = StringField("BankReference", validators=[Optional()])
    bank_status = SelectField("BankStatus", validators=[Optional()], choices=[])
    product_name = SelectField("CardName", validators=[InputRequired()],
                               choices=['CashBack', 'Etihad Guest Infinite Card'])
    bookingdate = DateField("BookingDate", validators=[Optional()])

    submit = SubmitField('Submit')

    #def validate_mobile(self, mobile):
        #if (current_user.userlevel=="1") & (request.method=="GET"):
            #mobile.type=HiddenField()
        #else:
            #mobile.validators=[DataRequired(), length(10,10)]



class Download(FlaskForm):
    start = DateField("StartDate", validators=[InputRequired()], format="%Y-%m-%d")
    end = DateField("EndDate", validators=[InputRequired()], format="%Y-%m-%d")
    stime=TimeField("StartTime")
    etime = TimeField("EndTime")
    download = SubmitField("Download")



class Upload(FlaskForm):
    upload = FileField("Upload", validators=[InputRequired()])
    uploadfile = SubmitField("UploadFile")

