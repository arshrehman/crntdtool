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



df = pd.read_csv('/var/www/html/datatoolserver/ddtool/static/files/all_countries.csv')
lst3 = list(df.iloc[:, 1])

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
            raise ValidationError("It must start with 784 and must have 15 digits")
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
            raise ValidationError("It must start with AE and must have 23 digits")
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length


ALLOWED_EXTENSIONS = set(['jpg','png','jpeg','pdf'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def file_extension2():
    def _length(form, field):
        x = field.data
        z=[]
        for a in x:
            z.append(secure_filename(a.filename))
        if z and len(re.findall(".",z[0]))>=1:
            for y in x:
                if y and allowed_file(y.filename):
                    pass
                else:
                    raise ValidationError("It must be a jpg, jpeg, png or pdf file")
        else:
            pass
    return _length


class Adcbleads(FlaskForm):
    # Customer's personal Details
    customer_name = StringField('Name', validators=[Optional(), Length(min=6, max=100)])
    gender = SelectField('Gender', validators=[Optional()],
                         choices=["MALE", "FEMALE"])
    nationality = SelectField('Nationality', validators=[Optional()], choices=lst3, default=1)
    dob = DateField('DOB', validators=[Optional()])
    passport_number = StringField('Passport', validators=[Optional()])
    passport_expiry = DateField("ExpireOn", validators=[Optional()])
    visa_number = StringField("VisaNumber", validators=[Optional()])
    visa_expiry_date = DateField("VisaExpiryDate", validators=[Optional()])
    emirates_id = IntegerField('EmiratesID', validators=[Optional()])
    # EID_expiry_date = DateField("ExpireOn", validators=[Optional()])
    length_of_residence = DecimalField("YearsInUAE", validators=[Optional()])
    marital_status = SelectField("MaritalStatus", validators=[Optional()], choices=['Single', 'Married', 'Other'])
    dependent = SelectField('NumberOfDependent', validators=[Optional()], choices=["0","1","2"]) #optional
    education = SelectField("Education", validators=[Optional()], choices=['Graduate', 'Post-Graduate', 'Other'])
    mothername = StringField("Mother's MaidenName", validators=[Optional()])

    # office Details

    company = StringField('Company', validators=[Optional(), Length(min=4, max=100)])
    # ale_status = SelectField("TML/NTML", validators=[Optional()], choices=["TML", "NTML"])
    office_emirates = SelectField("OfficeEmirates", validators=[Optional()],
                                  choices=["AbuDhabi", "AlAin", "Ajman", "Dubai", "Fujairah", "RasAlKhaima", "Sharjah",
                                           "UmmAlQuwain"])
    company_phone = StringField("CompanyPhoneNumber", validators=[Optional()])
    building = StringField("BuildingName", validators=[Optional()])
    area = StringField("Street/Area", validators=[Optional()])
    landmark = StringField("NearestLandmark", validators=[Optional()])

    """bankingwith=SelectField("SalaryAccount", validators=[Optional()], choices=["ADCB","ADIB", "ENBD", "MASHREQ", "RAK", "CBD", "SCB", "HSBC", "DIB",
                                                                                "FAB","CBI","EIB", "ALMASRAF","BANK OF SHARJAH",
                                                                               "UNITED ARAB BANK","CBI","NBF","NBQ",
                                                                               "SHARJAH ISLAMIC BANK","AL HILAL BANK","AJMAN BANK",
                                                                               "ARAB BANK","BANQUE MISR","BANK OF BARODA","NATIONAL BANK OF BAHRAIN","HBL","CITI",
                                                                               "BANK SEDARAT IRAN","BANK MELLI IRAN","UBL","DEUSTCHE BANK","NBK","BANK OF CHINA",
                                                                               "OTHER"])"""

    # if you are Salaried

    designation = StringField("Designation", validators=[Optional()])
    joiningdate = DateField("JoiningDate", validators=[Optional()])
    department = StringField("Department", validators=[Optional()])
    staffid = StringField('StaffID', validators=[Optional()])
    salary = DecimalField('Salary', validators=[Optional(), NumberRange(min=5000, max=150000)])

    # Mailing Address
    pobox = StringField("PO-Box", validators=[Optional()])


    # Contact Details
    mobile = StringField('Mobile', validators=[Optional()])
    customer_email = StringField('Email', validators=[Optional()])

    # Are you an ADCB account Holder.
    account_check = SelectField("DoYouHaveADCBAccount", validators=[Optional()], choices=['No', 'Yes'])

    # Home country Address
    homecountryaddress = StringField("Address", validators=[Optional()])
    city = StringField("City", validators=[Optional()])
    telephone = IntegerField("Contact", validators=[Optional()])

    # PersonalReferenceUAE
    reference_name = StringField('Name', validators=[Optional()])
    reference_company = StringField("CompanyName", validators=[Optional()])
    reference_mobile = IntegerField('Mobile', validators=[Optional()])

    # ResidentialAddress
    building2 = StringField("BuildingName", validators=[Optional()])
    flat = StringField("FlatNumber", validators=[Optional()])
    area2 = StringField("Street/Area", validators=[Optional()])
    landmark2 = StringField("NearestLandmark", validators=[Optional()])
    residential_emirates = SelectField("Emirates", validators=[Optional()],
                            choices=["AbuDhabi", "AlAin", "Ajman", "Dubai", "Fujairah", "RasAlKhaima", "Sharjah",
                                     "UmmAlQuwain"])
    residence_type = SelectField("ResidenceType", validators=[Optional()],
                                 choices=['Rented', 'Owned', 'EmployerProvided'])

    # iban = StringField("IBAN", validators=[Optional(), length4(23,23)])
    product_name = SelectField('ProductName', validators=[Optional()],
                               choices=["Betaqti Master Card World Elite", "Touch Points Visa Infinite",
                                        "Touch Points Visa Platinum"
                                   , "Touch Points Visa Gold", "Touch Points Mastercard Platinum",
                                        "Touch Points Visa Titanium", "All-ADCB Visa Infinite",
                                        "All-ADCB Visa Signature",
                                        "Lulu Mastercard Platinum", "Lulu Mastercard Titanium",
                                        "Etihad Guest Visa Infinite", "Etihad Guest Visa Signature",
                                        "Etihad Guest Visa Platinum",
                                        "Business Platinum", "Traveller Mastercard World",
                                        "Simplylife Family Visa Platinum", "Simplylife CashBack Titanium",
                                        "365 CashBack Visa Platinum", "Talabat Mastercard Platinum"])
    prefered_billing = SelectField("Preferred Billing Date", validators=[Optional()], choices=["5th", "10th", "19th", "24th"])

    pickupdate=DateField("Pickup Date", validators=[Optional()])
    pickupaddress=StringField("Pickup Address", validators=[Optional()])
    attachment3=MultipleFileField("EmiratesID,Passport,Visa", validators=[file_extension2()])
    """bank_reference = StringField("BankReference", validators=[Optional()])
    bank_status = SelectField("BankStatus", validators=[Optional()], choices=[], default="Inprocess")
    application_type=SelectField("ApplicationType", validators=[Optional()], choices=[])
    submissiondate = DateField("SubmissionDate", validators=[Optional()])
    bookingdate = DateField("BookingDate", validators=[Optional()])
    supplementary_card=SelectField("SupplCard", validators=[Optional()], choices=['NotRequired', 'Required'],default="NotRequired")
    remarks=TextAreaField("Remarks", validators=[Optional()])
    cpv=SelectField("CPV", validators=[Optional()])
    
    promo = SelectField("Promo", validators=[Optional()], choices=['AECB', 'NCC', 'STC', 'CHLD', 'EMRT'])
    last6salaries=SelectField("Last6Salaries", validators=[Optional()], choices=['YES', 'NO'])
    cbdsource = SelectField("Source", validators=[Optional()], choices=['DIRECT'])
    aecb=SelectField("AECB", validators=[Optional()], choices=['No-Hit', 'Enter AECB score'])"""

    submit2 = SubmitField('Submit')
