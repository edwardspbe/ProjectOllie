from flask import Flask, Response, render_template, request, redirect, session, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_dropzone import Dropzone
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = os.urandom(12)
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE='.txt',
    DROPZONE_MAX_FILES=1,
)
application = app

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = u"Sorry, you need to login to access this page!"
login_manager.session_protection = "strong"

dropzone = Dropzone(app)


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('index.html')


@app.route('/ollie', methods=['GET', 'POST'])
@login_required
def index():
    return '''<h1>What next?</h1>
              <ul>
                <li><a href='/upload'>Upload Files</a></li>
                <li><a href='/logout'>Logout</a></li>
                <li><a href='http://sandybeachatotterlake.com'>SandyBeachatOtterLake.com</a></li>
              </ul>
           '''

@app.route('/availability', methods=['GET',])
def avail():
    output = ""
    file = "availability.txt"
    if os.path.exists(file):
        with open(file) as f: 
            output = f.read()
    return output


class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "ollie" + str(id)
        self.password = self.name + "s_secret"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        uname = 'ollie'
        username = request.form['username']
        password = request.form['password']
        if username == 'ollie' and password == username + "s_secret":
            id = 1
            user = User(id)
            login_user(user)
            next = request.args.get("next")
            if next :
                return redirect(next)
            else :
                return index()
        else:
            return abort(401)
    else:
        return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('''
          <h3>Logged out!</h3>
          <p>Click the following <a href="/login">link</a> to log in...</p>
          ''' )

@app.errorhandler(401)
def page_not_found(e):
    return Response('''
          <h3>Login failed!</h3>
          <p>Click the following <a href="/login">link</a> to try again...</p>
          ''' )

# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__ == "__main__":
    app.run(debug=True)

