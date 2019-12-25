from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' 
# tells the application where our database will be stored

db = SQLAlchemy(app) 
# initialise connection to the database


class User(db.Model):  # create a new class which inherits from a basic database model, provided by SQLAlchemy
    # SQLAlchemy also creates a table called user, which it will use to store our User objects.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    
    # defines how to represent our User object as a string. This allows us to do things like print(User)
    def __repr__(self):
        return '<User %r>' % self.id


class ToDo(db.Model):
    # SQLAlchemy create a table called "toDo", which it will use to store our "ToDo" objects.
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id

class RegisterForm(Form):
    name = StringField('Name', validators=[validators.Length(min=1,max=50)])
    email = StringField('Email', validators=[validators.Length(min=1,max=50), validators.Email()])
    username = StringField('Username', validators=[validators.Length(min=4,max=30)])
    password = PasswordField('Password', 
        validators=[validators.InputRequired(), 
                    validators.EqualTo('confirm', message="Passwords do not match!")]) 
    confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    username = StringField('Username', validators=[validators.Length(min=4,max=30)])
    password = PasswordField('Password',validators=[validators.InputRequired()])


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'GET':
        form = RegisterForm()
        return render_template("register.html",form=form)
    else:
        form = RegisterForm(request.form)
        if form.validate():
            name = form.name.data
            email = form.email.data
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))
            new_user = User(name=name, email=email, username=username, password=passw)
            print("User created!")
            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
            except:
                return "There was an issue in adding this user in our database!"
        else:
            return "Form not valid!"

@app.route("/allusers")
def allusers():
    all_users = User.query.order_by(User.id).all()
    return render_template("all_users.html", all_users = all_users)


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        return render_template("login.html", form=form)
    else:
        form = LoginForm(request.form)
        if form.validate():
            name = form.username.data
            # passw = sha256_crypt.encrypt(str(form.password.data))
            passw = form.password.data
            try:
                user = User.query.filter_by(username=name)
                if user!=NULL and sha256_crypt.verify(passw, user.password):
                    session.logged_in = True
                    return redirect(url_for('home'),current_user=user)
                else:
                    # return redirect(url_for('register'))
                    return "User not valid!"
            except:
                # return redirect(url_for('register'))
                return "Error occured in filtering"
        else:
            return "Form not validated!"
        


@app.route("/logout")
def logout():
    session.logged_in = False
    return render_template("home.html")


@app.route("/tasks/<int:id>", methods = ['GET','POST'])
def tasks(id):
    if request.method == 'GET':
        current_tasks = ToDo.query.filter_by(user_id=id).order_by(ToDo.date_created)
        return render_template("tasks.html", tasks = current_tasks)
    else:
        task_content = request.form['content']
        new_task = ToDo(content=task_content, user_id=id)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/tasks")
        except:
            return "There was an issue adding the new task to our database!"


@app.route("/deleteTask/<int:id>")
def delete(id):
    task_to_delete = ToDo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/tasks")
    except:
        return "There was an issue deleting that task!"


@app.route("/updateTask/<int:id>", methods=['GET','POST'])
def update(id):
    task_to_update = ToDo.query.get_or_404(id)
    if request.method == 'GET':
        return render_template("updateTask.html", task = task_to_update)
    else:
        new_content = request.form['content']
        task_to_update.content = new_content
        try:
            db.session.commit()
            return redirect("/tasks")
        except:
            return "There was an issue updating that task!"


if __name__ == "__main__":
    app.run(debug=True)



# command to enter the virtual environment :
# source env/bin/activate

# command to create the db :
# python (will open python3 shell)
# from app import db
# db.create_all()