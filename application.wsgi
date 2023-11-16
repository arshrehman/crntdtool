import sys
sys.path.insert(0, "/var/www/html/datatoolserver")
activate_this="/home/ubuntu/.local/share/virtualenvs/datatoolserver-28lNwDdb/bin/activate_this.py"
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
from application import app as application
