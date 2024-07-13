from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from datetime import datetime

import os
from dotenv import load_dotenv


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
migrate = Migrate(app, db)

# Create Model
class Tasks(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  task = db.Column(db.String(100), nullable=False)
  description = db.Column(db.String(200), nullable=False)
  priority = db.Column(db.Unicode(100), nullable=False)
  date_added = db.Column(db.DateTime, default=datetime.utcnow)

  # Create A String
  def __repr__(self):
    return '<Task %r>' % self.task
  
# Create a Form Class
class AddForm(FlaskForm):
  task = StringField("Name of Task", validators=[DataRequired()])
  description = StringField("Description of Task", validators=[DataRequired()])
  priority = SelectField("Priority of Task", choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], validators=[DataRequired()])
  submit = SubmitField("Submit")

# Create an Update Form
class UpdateForm(FlaskForm):
  task = StringField("Edit Task", validators=[DataRequired()])
  description = StringField("Edit Description", validators=[DataRequired()])
  priority = SelectField("Priority of Task", choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], validators=[DataRequired()])
  submit = SubmitField("Submit")

# Delete Database Record
@app.route('/delete/<int:id>')
def delete(id):
  task_to_delete = Tasks.query.get_or_404(id)
  task = None
  form = AddForm()

  try:
    db.session.delete(task_to_delete)
    db.session.commit()
    flash("Task Deleted Successfully!")
    our_tasks=Tasks.query.order_by(Tasks.date_added)
    return render_template('task.html',
      task = task,
      form = form,
      our_tasks=our_tasks)

  except:
    flash("Whoops! There was a problem deleting task, try again...")
    return render_template('task.html',
      task = task,
      form = form,
      our_tasks=our_tasks)

# Update Database Record
@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
  form = UpdateForm()
  task_to_update = Tasks.query.get_or_404(id)
  if request.method == "POST":
    task_to_update.task = request.form['task']
    task_to_update.description = request.form['description']
    task_to_update.priority = request.form['priority']
    try:
      db.session.commit()
      flash('Task Updated Successfully!')
      return render_template("update.html",
        form=form,
        task_to_update=task_to_update)
    except:
      flash('Error! Looks like there was a problem... Try Again!')
      return render_template("update.html",
        form=form,
        task_to_update=task_to_update,
        id=id)
  else:
    return render_template("update.html",
        form=form,
        task_to_update=task_to_update,
        id=id)

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
  priority = None

  form = AddForm()
  # Validate Form
  if form.validate_on_submit():
    task = form.task.data
    description = form.description.data
    priority = form.priority.data

    new_task = Tasks(task=form.task.data, description=form.description.data, priority=form.priority.data)
    db.session.add(new_task)
    db.session.commit()

    flash("Task Added Successfully!")
  our_tasks=Tasks.query.order_by(Tasks.date_added)
  return render_template('task.html',
    task = task,
    form = form,
    our_tasks=our_tasks)