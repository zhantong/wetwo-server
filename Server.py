from flask import Flask, request, render_template, redirect, jsonify
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
    password = request.form['password']
    if user_name and password and wetwo.is_password_correct(user_name=user_name, password=password):
        user_id = wetwo.get_user_id(user_name)
        user = User()
        user.id = user_id
        flask_login.login_user(user)
        return 'Login Success'
    return 'Bad Login'


@app.route('/api/login', methods=['POST'])
def api_login():
    user_name = request.form['name']
    password = request.form['password']
    if user_name and password and wetwo.is_password_correct(user_name=user_name, password=password):
        user_id = wetwo.get_user_id(user_name)
        user = User()
        user.id = user_id
        flask_login.login_user(user)
        return jsonify({'status': True, 'message': '登录成功'})
    return jsonify({'status': False, 'message': '登录失败'})


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


@app.route('/api/logout')
def api_logout():
    flask_login.logout_user()
    return jsonify({'status': True, 'message': '注销成功'})


@app.route('/')
@flask_login.login_required
def index():
    articles = wetwo.get_articles()
    for article in articles:
        article['comments'] = wetwo.get_comments(article['article_id'])
    return render_template('index.html', articles=articles)


@app.route('/api/getUserInfo')
@flask_login.login_required
def api_get_user_info():
    user_id = flask_login.current_user.id
    user_name = wetwo.get_user_name(user_id)
    info = {
        'id': user_id,
        'name': user_name
    }
    return jsonify(info)


@app.route('/api/getAllArticles')
@flask_login.login_required
def api_get_all_articles():
    offset = request.args['offset'] if 'offset' in request.args else 0
    limit = request.args['limit'] if 'limit' in request.args else 20
    articles = wetwo.get_articles(offset=offset, limit=limit)
    for article in articles:
        article['comments'] = wetwo.get_comments(article['article_id'])
    return jsonify(articles)


@app.route('/api/getArticles')
@flask_login.login_required
def api_get_articles():
    user_id = flask_login.current_user.id
    articles = wetwo.get_articles(user_id)
    for article in articles:
        article['comments'] = wetwo.get_comments(article['article_id'])
    return jsonify(articles)


@app.route('/api/getArticle')
@flask_login.login_required
def api_get_article():
    article_id = request.args['articleId']
    article = wetwo.get_article(article_id)
    article['comments'] = wetwo.get_comments(article['article_id'])
    return jsonify(article)


@app.route('/postArticle', methods=['POST'])
@flask_login.login_required
def post_article():
    article = request.form['article']
    user_id = flask_login.current_user.id
    article_id = wetwo.post_article(article, user_id)
    return redirect('/')


@app.route('/api/postArticle', methods=['POST'])
@flask_login.login_required
def api_post_article():
    article = request.form['article']
    time = request.form['time'] if 'time' in request.form else None
    user_id = flask_login.current_user.id
    article_id = wetwo.post_article(article, user_id, time)
    return jsonify({'status': True, 'articleId': article_id})


@app.route('/postComment', methods=['POST'])
@flask_login.login_required
def post_comment():
    article_id = request.form['articleId']
    comment = request.form['comment']
    parent_comment_id = request.form['parentCommentId']
    user_id = flask_login.current_user.id
    wetwo.post_comment(article_id, user_id, comment, parent_comment_id)
    article = wetwo.get_article(article_id)
    article['comments'] = wetwo.get_comments(article_id)
    return render_template('comment.html', article=article)


@app.route('/api/postComment', methods=['POST'])
@flask_login.login_required
def api_post_comment():
    article_id = request.form['articleId']
    comment = request.form['comment']
    parent_comment_id = request.form['parentCommentId']
    time = request.form['time'] if 'time' in request.form else None
    user_id = flask_login.current_user.id if 'userId' not in request.form else request.form['userId']
    print(article_id, user_id, comment, parent_comment_id, time)
    comment_id = wetwo.post_comment(article_id, user_id, comment, parent_comment_id, time)
    return jsonify({'status': True, 'commentId': comment_id})


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
