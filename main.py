from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# Create a Flask Instance
app = Flask(__name__)
app.app_context().push()

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{os.getenv("SQL_PASSWORD")}@localhost/tasks'

# Secret Key!
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Initialize the Database
db = SQLAlchemy(app)

# Create Model
class Tasks(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  task = db.Column(db.String(100), nullable=False)
  description = db.Column(db.String(200), nullable=False)
  date_added = db.Column(db.DateTime, default=datetime.utcnow)

  # Create A String
  def __repr__(self):
    return '<Task %r>' % self.task

# Create a Form Class
class TaskForm(FlaskForm):
  task = StringField("Name of Task", validators=[DataRequired()])
  description = StringField("Description of Task", validators=[DataRequired()])
  submit = SubmitField("Submit")

# Create a route decorator
@app.route('/')
def index():
  return render_template('index.html')

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html')

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
  return render_template('500.html')

# Create Task Page
@app.route('/task/add', methods=['GET','POST'])
def add_task():
  task = None
  description = None
  form = TaskForm()
  # Validate Form
  if form.validate_on_submit():
    task = form.task.data
    description = form.description.data

    new_task = Tasks(task=form.task.data, description=form.description.data)
    db.session.add(new_task)
    db.session.commit()

    flash("Task Added Successfully!")
  our_tasks=Tasks.query.order_by(Tasks.date_added)
  return render_template('task.html',
    task = task,
    form = form,
    our_tasks=our_tasks)