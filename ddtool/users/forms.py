from flask_wtf import FlaskForm
from wtforms import Form, DateTimeField, SubmitField, StringField, PasswordField, BooleanField, IntegerField, \
    SelectField, ValidationError, DateField, FileField,DecimalField,TextAreaField
from wtforms.validators import InputRequired, Length, Regexp, DataRequired, Optional



def length2(min=-1, max=-1):
    message = 'Must be between %d and %d characters long.' % (min, max)

    def _length(form, field):
        x = field.data
        if not x.isalnum():
            raise ValidationError("It must be combination of alphabets and numbers")
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length



def length3(min=-1, max=-1):
    message = 'Must be between %d and %d characters long.' % (min, max)

    def _length(form, field):
        x = field.data
        if not x.isdigit():
            raise ValidationError("Only numbers are allowed")
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')
    signin=SubmitField('Sign In')


class Create(FlaskForm):
    username = StringField("UserName", validators=[InputRequired()])
    password = StringField("Password", validators=[InputRequired(), length2(8,16)])
    hrmsid=StringField("AgntHRMS", validators=[InputRequired(), length3(5,6)])
    department = SelectField("Department", validators=[Optional()], choices=['ENBD', 'EIB', 'RAK', 'ADCB', 'SCB', 'CBD', 'ALHILAL'])
    name = StringField("AgentName", validators=[InputRequired()])
    location = SelectField("Location", validators=[Optional()], choices=['ABU DHABI', 'ALAIN', 'DUBAI', 'RAK', 'FUJAIRAH', 'SHARJAH', 'AJMAN'])
    usergroup = SelectField("UserGroup", validators=[Optional()], choices=["1","2","3","4"])
    tlhrmsid = StringField("TLhrms", validators=[Optional(), length3(5,6)])
    tlname = StringField("TL-Name", validators=[Optional()])
    mngrhrmsid=StringField("MngrHRMS", validators=[Optional(), length3(5,6)])
    manager = StringField("MngrName", validators=[Optional()])
    crdntrhrmsid=StringField("CrdntrID", validators=[InputRequired(), length3(5,6)])
    bankcode=StringField("BankCode", validators=[Optional()])

    CreateUser=SubmitField("CreateUser")
