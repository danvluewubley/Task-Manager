from flask import Flask, render_template

app = Flask(__name__)

# main cite
@app.route('/')
def index():
  return render_template('index.html')

# localhost:5000/user/name
@app.route('/user/<name>')
def user(name):
  return render_template('user.html', name=name)

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html')

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
  return render_template('500.html')