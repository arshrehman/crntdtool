import os
from dotenv import load_dotenv
import mysql.connector as mysql

load_dotenv()
naomi=os.environ.get('naomi')
db_pass=os.environ.get('db_pass')
UPLOADS_FOLDER = "/home/afzal/PycharmProjects/test_layout/ddtool/static/files"


class Config:
    SECRET_KEY = str(naomi)
    UPLOADS_FOLDER = UPLOADS_FOLDER
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://afzal:Automata&(ai)#1920@ddtool.c57mquvfyeii.eu-north-1.rds.amazonaws.com/ddtool'
