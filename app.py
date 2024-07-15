from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, PasswordField
from wtforms.validators import DataRequired, Email
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, Email, EqualTo, Length
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


# Create Task Model
class Tasks(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  task = db.Column(db.String(100), nullable=False)
  description = db.Column(db.String(200), nullable=False)
  priority = db.Column(db.Unicode(100), nullable=False)
  due_date = db.Column(db.String(100), nullable=False)
  date_added = db.Column(db.DateTime, default=datetime.utcnow)
  # Create A String
  def __repr__(self):
    return '<Task %r>' % self.task

# Create a Task Create Form
class AddTaskForm(FlaskForm):
  task = StringField("Name of Task", validators=[DataRequired()])
  description = StringField("Description of Task", validators=[DataRequired()])
  priority = SelectField("Priority of Task", choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], validators=[DataRequired()])
  due_date = DateField("Due Date of Task")
  submit = SubmitField("Submit")

# Create an Task Update Form
class UpdateTaskForm(FlaskForm):
  task = StringField("Edit Task", validators=[DataRequired()])
  description = StringField("Edit Description", validators=[DataRequired()])
  priority = SelectField("Priority of Task", choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], validators=[DataRequired()])
  due_date = DateField("Due Date of Task")
  submit = SubmitField("Submit")

# Create User Model
class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(200), nullable=False, unique=True)
  date_added = db.Column(db.DateTime, default=datetime.utcnow)

  # Password Hashing
  password_hash = db.Column(db.String(128))

  @property
  def password(self):
    raise AttributeError('Password is not a readable attribute!')
  
  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)
  
  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)

  # Create A String
  def __repr__(self):
    return '<Users %r>' % self.user

# Create a User Form Class
class AddUserForm(FlaskForm):
  name = StringField("Name", validators=[DataRequired()])
  email = StringField("Email", validators=[Email()])
  password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match')])
  password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
  submit = SubmitField("Submit")

# Create an User Update Form
class UpdateUserForm(FlaskForm):
  name = StringField("Edit Name", validators=[DataRequired()])
  email = StringField("Edit Email", validators=[Email()])
  submit = SubmitField("Submit")

# Create Task Page
@app.route('/task/add', methods=['GET','POST'])
def add_task():
  task = None
  description = None
  priority = None
  due_date = None

  form = AddTaskForm()
  # Validate Form
  if form.validate_on_submit():
    task = form.task.data
    description = form.description.data
    priority = form.priority.data
    due_date = form.priority.data

    new_task = Tasks(task=form.task.data, description=form.description.data, priority=form.priority.data, due_date=form.due_date.data)
    db.session.add(new_task)
    db.session.commit()

    flash("Task Added Successfully!")
  our_tasks=Tasks.query.order_by(Tasks.due_date)
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
    task_to_update.due_date = request.form['due_date']
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
    our_tasks=Tasks.query.order_by(Tasks.due_date)
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
  name = None
  email = None
  password_hash = None

  form = AddUserForm()
  # Validate Form
  if form.validate_on_submit():
    name = form.name.data
    email = form.email.data
    password_hash = form.password_hash.data

    form.name.data = ''
    form.email.data = ''
    form.password_hash.data = ''

    # Hash the password
    hashed_pw = generate_password_hash(password_hash, method="pbkdf2")

    new_user = Users(name=name, email=email, password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    flash("User Added Successfully!")

  our_users=Users.query.order_by(Users.date_added)
  return render_template('user.html',
    name = name,
    form = form,
    our_users=our_users)


# Update Database Record
@app.route('/user/update/<int:id>',methods=['GET','POST'])
def user_update(id):
  form = UpdateUserForm()
  user_to_update = Users.query.get_or_404(id)
  if request.method == "POST":
    user_to_update.name = request.form['name']
    user_to_update.email = request.form['email']
    try:
      db.session.commit()
      flash('User Updated Successfully!')
      return render_template("edit_user.html",
        form=form,
        user_to_update=user_to_update)
    except:
      flash('Error! Looks like there was a problem... Try Again!')
      return render_template("edit_user.html",
        form=form,
        user_to_update=user_to_update,
        id=id)
  else:
    return render_template("edit_user.html",
        form=form,
        user_to_update=user_to_update,
        id=id)


# Delete Database Record
@app.route('/user/delete/<int:id>')
def user_delete(id):
  user_to_delete = Users.query.get_or_404(id)
  name = None
  form = AddUserForm()

  try:
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("User Deleted Successfully!")
    our_users=Users.query.order_by(Users.date_added)
    return render_template('user.html',
      name = name,
      form = form,
      our_users=our_users)

  except:
    flash("Whoops! There was a problem deleting user, try again...")
    return render_template('user.html',
      name = name,
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