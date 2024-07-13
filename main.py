from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email

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
app.config['SQLALCHEMY_BINDS'] = {
  'users': f'mysql+pymysql://root:{os.getenv("SQL_PASSWORD")}@localhost/users'
  }

# Secret Key!
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Initialize the Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Create Task Model
class Tasks(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  task = db.Column(db.String(100), nullable=False)
  description = db.Column(db.String(200), nullable=False)
  priority = db.Column(db.Unicode(100), nullable=False)
  date_added = db.Column(db.DateTime, default=datetime.utcnow)

  # Create A String
  def __repr__(self):
    return '<Task %r>' % self.task
  
# Create a Task Create Form
class AddTaskForm(FlaskForm):
  task = StringField("Name of Task", validators=[DataRequired()])
  description = StringField("Description of Task", validators=[DataRequired()])
  priority = SelectField("Priority of Task", choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], validators=[DataRequired()])
  submit = SubmitField("Submit")

# Create an Task Update Form
class UpdateTaskForm(FlaskForm):
  task = StringField("Edit Task", validators=[DataRequired()])
  description = StringField("Edit Description", validators=[DataRequired()])
  priority = SelectField("Priority of Task", choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], validators=[DataRequired()])
  submit = SubmitField("Submit")

# Create User Model
class Users(db.Model):
  __bind_key__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  user = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(200), nullable=False, unique=True)
  date_added = db.Column(db.DateTime, default=datetime.utcnow)

  # Create A String
  def __repr__(self):
    return '<Users %r>' % self.user
  
# Create a User Form Class
class AddUserForm(FlaskForm):
  __bind_key__ = 'users'
  user = StringField("User", validators=[DataRequired()])
  email = StringField("Email", validators=[Email()])
  submit = SubmitField("Submit")

# Create an User Update Form
class UpdateUserForm(FlaskForm):
  __bind_key__ = 'users'
  user = StringField("Edit User", validators=[DataRequired()])
  email = StringField("Edit Email", validators=[Email()])
  submit = SubmitField("Submit")

# Create Task Page
@app.route('/task/add', methods=['GET','POST'])
def add_task():
  task = None
  description = None
  priority = None

  form = AddTaskForm()
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

# Update Database Record
@app.route('/task/update/<int:id>',methods=['GET','POST'])
def task_update(id):
  form = UpdateTaskForm()
  task_to_update = Tasks.query.get_or_404(id)
  if request.method == "POST":
    task_to_update.task = request.form['task']
    task_to_update.description = request.form['description']
    task_to_update.priority = request.form['priority']
    try:
      db.session.commit()
      flash('Task Updated Successfully!')
      return render_template("update_task.html",
        form=form,
        task_to_update=task_to_update)
    except:
      flash('Error! Looks like there was a problem... Try Again!')
      return render_template("update_task.html",
        form=form,
        task_to_update=task_to_update,
        id=id)
  else:
    return render_template("update_task.html",
        form=form,
        task_to_update=task_to_update,
        id=id)

# Delete Database Record
@app.route('/task/delete/<int:id>')
def task_delete(id):
  task_to_delete = Tasks.query.get_or_404(id)
  task = None
  form = AddTaskForm()

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



# Create User Page
@app.route('/user/add', methods=['GET','POST'])
def add_user():
  user = None
  email = None

  form = AddUserForm()
  # Validate Form
  if form.validate_on_submit():
    user = form.user.data
    email = form.email.data

    new_user = Users(user=user, email=email)
    db.session.add(new_user)
    db.session.commit()

    flash("User Added Successfully!")
    
  our_users=Users.query.order_by(Users.date_added)
  return render_template('user.html',
    user = user,
    form = form,
    our_users=our_users)

# Update Database Record
@app.route('/user/update/<int:id>',methods=['GET','POST'])
def user_update(id):
  form = UpdateUserForm()
  user_to_update = Users.query.get_or_404(id)
  if request.method == "POST":
    user_to_update.user = request.form['user']
    user_to_update.email = request.form['email']
    try:
      db.session.commit()
      flash('User Updated Successfully!')
      return render_template("update_user.html",
        form=form,
        user_to_update=user_to_update)
    except:
      flash('Error! Looks like there was a problem... Try Again!')
      return render_template("update_user.html",
        form=form,
        user_to_update=user_to_update,
        id=id)
  else:
    return render_template("update_user.html",
        form=form,
        user_to_update=user_to_update,
        id=id)

# Delete Database Record
@app.route('/user/delete/<int:id>')
def user_delete(id):
  user_to_delete = Users.query.get_or_404(id)
  user = None
  form = AddUserForm()

  try:
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("User Deleted Successfully!")
    our_users=Users.query.order_by(Users.date_added)
    return render_template('user.html',
      user = user,
      form = form,
      our_users=our_users)

  except:
    flash("Whoops! There was a problem deleting task, try again...")
    return render_template('user.html',
      user = user,
      form = form,
      our_users=our_users)


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