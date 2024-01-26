"""
Basic flask server

running at 'localhost:5000'
.Net Ninjas - 3/12/2021
Ellie Bruhns, Yifeng Cui, Cameron Jordal, Isaac Priddy, Nick Titzler
"""
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import queries as db
from forms import LoginForm, ResourceForm
import logging
from secrets import token_hex
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
#import config


############
# Globals
############

app = Flask(__name__)
app.config["SECRET_KEY"] = str(token_hex(16))
login_manager = LoginManager()
login_manager.init_app(app)
DEBUG = True


#################
# Set User Ids
#################

# TODO: TURN THIS INTO A DATABASE
# TODO: hash passwords
# local password database
student_db = {
    "admin": "password"
}
teacher_db = {
    "admin": "password"
}
# get all student and teacher ids
idList = db.GeneralUse().fetch_all_student_ids()
tidList = db.GeneralUse().fetch_all_teacher_ids()
# give all ids the password "password"
for item in idList:
    student_db[str(item)] = "password"
for item in tidList:
    teacher_db[str(item)] = "password"


######################
# Session Management
######################

class User(UserMixin):
    """Simple user class for managing user logins."""
    def __init__(self, user_id):
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    """A callback function for loading in current user."""
    return User(user_id)

@login_manager.unauthorized_handler
def unauthorized_callback():
    """Function for redirecting requests to pages when
    authorization is not met."""
    flash("Login Required.", "danger")
    return redirect("/login")


#################
# Site Serving
#################

@app.route("/")
@app.route("/home")
def home():
    """Home page of website."""
    app.logger.debug("accessing main page")
    # grab all available book in database
    book_list = db.GeneralUse().fetch_all_books()
    return render_template('home.html', books=book_list)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page of website."""
    # prevent logged-in users from going back to login page
    if current_user.is_authenticated:
        return redirect("/")
    app.logger.debug("accessing login page")
    login_form = LoginForm()
    # TODO: ADD CSRF CERT
    # TODO: MAKE THINGS SECURE
    # when a form is submitted
    if login_form.is_submitted():
        # check if valid student username
        if login_form.username.data in student_db.keys():
            # check if valid password
            if login_form.password.data == student_db[login_form.username.data]:
                # login student
                user = User(login_form.username.data)
                login_user(user, remember=login_form.remember.data)
                return redirect(url_for("student"))
        # check if valid teacher username when not valid student username
        elif login_form.username.data in teacher_db.keys():
            # check if valid password
            if login_form.password.data == teacher_db[login_form.username.data]:
                # login teacher
                user = User(login_form.username.data)
                login_user(user, remember=login_form.remember.data)
                return redirect(url_for("teacher"))
        # otherwise, show message indicating invalid entry
        flash("Invalid username and/or password provided.", "danger")
    return render_template('login.html', form=login_form)

@app.route("/logout")
def logout():
    """Logout page for website."""
    # prevent logged out users from logging out
    if not current_user.is_authenticated:
        return redirect("/")
    logout_user()
    return redirect("/home")

@app.route("/about")
def about():
    """About page for website."""
    app.logger.debug("accessing about page")
    return render_template('about.html')

@app.route("/student")
@login_required
def student():
    """Student page of website."""
    # TODO: BLOCK ACCESS FROM TEACHERS
    app.logger.debug("accessing student page")
    # grab student user access object
    curr_user_db = db.StudentSqlCommands(current_user.id)
    # grab current classes
    student_classes = curr_user_db.return_classes()
    # grab assigned books for each class
    student_books = {}
    for s_class in student_classes:
        class_crn = s_class[0][0]
        class_name = s_class[0][3]
        student_books[class_name] = curr_user_db.return_books(class_crn)
    return render_template('student.html', books=student_books)

@app.route("/teacher", methods=["GET", "POST"])
@login_required
def teacher():
    """Teacher page of website."""
    # TODO: BLOCK ACCESS FROM STUDENTS
    app.logger.debug("accessing teacher page")
    # grab teacher user access object
    curr_user_db = db.TeacherSqlCommands(current_user.id)
    # grab current classes
    teacher_classes = curr_user_db.return_classes()
    # grab books for each class
    teacher_books = {}
    for t_class in teacher_classes:
        class_crn = t_class[0][0]
        class_name = t_class[0][3]
        teacher_books[class_name] = curr_user_db.return_books(class_crn)
    # create form for adding and removing books from classes
    resource_form = ResourceForm()
    # when form is submitted
    if resource_form.is_submitted():
        # add isbn to crn when option to add book is selected
        if resource_form.action.data == "add":
            app.logger.debug("adding class")
            curr_user_db.add_book(resource_form.crn.data, resource_form.isbn.data)
        # otherwise must be remove option, so remove isbn from crn
        else:
            app.logger.debug("removing class")
            curr_user_db.remove_book(resource_form.crn.data, resource_form.isbn.data)
    return render_template('teacher.html', books=teacher_books, form=resource_form)

@app.route("/icons/person.svg")
def anonymous_icon():
    """Access point for image of person."""
    f_name = "resources/icons/person.svg"
    return send_file(f_name)


if __name__ == "__main__":
    app.run(debug=DEBUG)
