from flask import Flask, request, render_template, redirect, url_for
import flask_login
from WeTwo import WeTwo

app = Flask(__name__)
app.secret_key = '\xecG>\xc3\xe6\xe5\xbds\xa5\xf1\xae\x81u\x19\xb0`\x88W\xc6\\\xb7\xfeL\xcc'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class User(flask_login.UserMixin):
    pass


wetwo = WeTwo()


@login_manager.user_loader
def user_loader(user_id):
    if not wetwo.is_user_id_exists(user_id):
        return
    user = User()
    user.id = user_id
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    user_name = request.form['name']
    if user_name:
        user_id = wetwo.get_user_id(user_name)
        if wetwo.is_user_id_exists(user_id):
            password = request.form['password']
            if wetwo.is_password_correct(user_id, password):
                user = User()
                user.id = user_id
                flask_login.login_user(user)
                return 'Login Success'
    return 'Bad Login'


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


@app.route('/')
@flask_login.login_required
def index():
    return render_template('index.html')


@app.route('/postArticle', methods=['POST'])
@flask_login.login_required
def post_article():
    article = request.form['article']
    user_id = flask_login.current_user.id
    article_id = wetwo.post_article(article, user_id)
    return redirect('/')


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
