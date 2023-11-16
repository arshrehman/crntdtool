import datetime
from ddtool import db
from ddtool import db
from flask_login import UserMixin
from ddtool import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80))
    agent_name=db.Column(db.String(50))
    hrmsID = db.Column(db.String(10))
    bankcode=db.Column(db.String(20))
    bankname = db.Column(db.String(10))
    tlhrmsid=db.Column(db.String(10))
    tlname=db.Column(db.String(50))
    manager = db.Column(db.String(30))
    mngrhrmsid = db.Column(db.String(30))
    coordinator_hrmsid =db.Column(db.String(30))
    location = db.Column(db.String(30))
    userlevel = db.Column(db.String(10))
    reins2=db.relationship('Reins2', back_populates='user')

class Reins2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bankcode=db.Column(db.String(20))
    bankref=db.Column(db.String(40))
    customer_name=db.Column(db.String(150))
    company=db.Column(db.String(150))
    date=db.Column(db.DateTime, default=datetime.datetime.now())
    rejection=db.Column(db.Text)
    justification=db.Column(db.String(500))
    doc_path=db.Column(db.String(100))
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user=db.relationship('User', back_populates='reins2')    

class Adcb(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    entry_date=db.Column(db.DateTime, default=datetime.datetime.now())
    product_name=db.Column(db.String(100))
    customer_name=db.Column(db.String(200))
    mobile=db.Column(db.String(20))
    gender=db.Column(db.String(20))
    nationality=db.Column(db.String(20))
    dob=db.Column(db.DateTime)
    passport_number=db.Column(db.String(50))
    passport_expiry=db.Column(db.DateTime)
    visa_number=db.Column(db.String(50))
    visa_expiry_date=db.Column(db.DateTime)
    emirates_id=db.Column(db.String(30))
    length_of_residence=db.Column(db.String(10))
    marital_status=db.Column(db.String(10))
    dependent=db.Column(db.String(10))
    education=db.Column(db.String(10))
    mothername=db.Column(db.String(50))
    company=db.Column(db.String(80))
    office_emirates=db.Column(db.String(50))
    company_phone=db.Column(db.String(50))
    building=db.Column(db.String(50))
    area=db.Column(db.String(150))
    landmark=db.Column(db.String(150))
    designation=db.Column(db.String(150))
    joiningdate=db.Column(db.DateTime)
    department=db.Column(db.String(150))
    staffid=db.Column(db.String(100))
    salary=db.Column(db.String(100))
    customer_email=db.Column(db.String(100))
    account_check=db.Column(db.String(100))
    homecountryaddress=db.Column(db.String(100))
    city=db.Column(db.String(50))
    telephone=db.Column(db.String(50))
    reference_name=db.Column(db.String(50))
    reference_company=db.Column(db.String(100))
    reference_mobile=db.Column(db.String(50))
    building2=db.Column(db.String(50))
    area2=db.Column(db.String(150))
    landmark2=db.Column(db.String(100))
    residence_type=db.Column(db.String(20))
    residential_emirates=db.Column(db.String(50))
    prefered_billing=db.Column(db.String(20))
    pickupdate=db.Column(db.DateTime)
    pickupaddress=db.Column(db.String(200))
    attachment=db.Column(db.String(200))
    user_id=db.Column(db.Integer)


class Reinstate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rejection=db.Column(db.String(1000))
    justification=db.Column(db.String(500))
    doc_path=db.Column(db.String(100))
    appdata_id=db.Column(db.Integer, db.ForeignKey('appdata.id'))
    date=db.Column(db.DateTime, default=datetime.datetime.now())
    appdata=db.relationship('Appdata', uselist=False, back_populates='reinstate')
    


    
class Appdata(db.Model):
    #primary columns
    id = db.Column(db.Integer, primary_key=True)
    leadid=db.Column(db.String(30))
    entry_date = db.Column(db.DateTime, nullable=False)

    #agent detection
    agent_id = db.Column(db.String(20), nullable=False) #will be fetched by session user
    agent_name = db.Column(db.String(100)) #will be fetched by session user
    tlhrmsid = db.Column(db.String(100)) #will be fetched by session user
    mngrhrmsid=db.Column(db.String(50))
    crdntr_hrmsid=db.Column(db.String(50))
    agent_location = db.Column(db.String(60)) #will be fetched by session user
    agent_level=db.Column(db.String(10)) #will be fetched by session user

    #Primary customer information
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(200))
    gender = db.Column(db.String(10), default="M")
    mobile = db.Column(db.String(20))
    dob = db.Column(db.DateTime)
    salary = db.Column(db.Float)
    nationality = db.Column(db.String(50))
    company = db.Column(db.String(100))
    designation = db.Column(db.String(50))
    ale_status = db.Column(db.String(10))
    office_emirates = db.Column(db.String(100))
    length_of_residence = db.Column(db.String(10))
    length_of_service = db.Column(db.String(10))

    #Secondary customer informatio
    emirates_id = db.Column(db.String(30))
    EID_expiry_date = db.Column(db.DateTime)
    passport_number = db.Column(db.String(10))
    passport_expiry = db.Column(db.DateTime)
    cheque_number = db.Column(db.String(100))
    cheque_bank = db.Column(db.String(100))
    iban = db.Column(db.String(100))
    bankingwith=db.Column(db.String(50))
    visa_expiry_date = db.Column(db.DateTime)
    submissiondate=db.Column(db.DateTime)
    bookingdate=db.Column(db.DateTime)

    # Bank specific group
    bank_name = db.Column(db.String(50))  # Will be fetched by session user
    product_type = db.Column(db.String(100))  # Depends on bank name
    product_name = db.Column(db.String(100))  # Depends on bank name
    bank_reference = db.Column(db.String(100))  # Depends on bank name
    bank_status = db.Column(db.String(100))   # Depends on bank name
    application_type = db.Column(db.String(50))
    supplementary_card = db.Column(db.String(50))
    remarks = db.Column(db.String(500))
    cpv = db.Column(db.String(100))

    # Al Hilal bank specific
    cclimit = db.Column(db.String(90))
    mothername = db.Column(db.String(90))
    uaeaddress = db.Column(db.String(300))
    homecountryaddress = db.Column(db.String(300))
    homecountrynumber = db.Column(db.String(20))
    joiningdate = db.Column(db.DateTime)
    ref1name = db.Column(db.String(100))
    ref2name = db.Column(db.String(100))
    ref1mobile = db.Column(db.String(100))
    ref2mobile = db.Column(db.String(100))
    sent = db.Column(db.DateTime)
    promo = db.Column(db.String(100))
    bankcode2=db.Column(db.String(20))
    docaddress=db.Column(db.String(500))
    contactoffice=db.Column(db.String(50))

    # CBD bank specific
    last6salaries=db.Column(db.String(10))
    cbdsource=db.Column(db.String(20))

    #ENBD specific
    aecb=db.Column(db.String(20))

    #relation with reinstate
    reinstate=db.relationship('Reinstate', uselist=False, back_populates='appdata')