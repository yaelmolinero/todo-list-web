from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import asc
from werkzeug.security import generate_password_hash, check_password_hash
from shortuuid import ShortUUID
from functools import wraps
from secrets import token_hex
from datetime import date
from forms import RegisterUser, LoginUser

app = Flask(__name__)
app.config["SECRET_KEY"] = token_hex(32)

# -------------------- CONFIG DB -------------------- #
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///list_todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# -------------------- CONFIG LOGIN -------------------- #
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# -------------------- CONFIG ADMIN -------------------- #
def admin_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.get_id() == "1":
            return func(*args, **kwargs)
        return abort(403)

    return decorated_function

# -------------------- DATABASE TABLES STRUCTURE -------------------- #
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    saved_lists = relationship("List", back_populates="list_author")

    def __repr__(self):
        return f"<User: {self.email}>"


class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), unique=True, nullable=False)
    is_saved = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    list_author = relationship("User", back_populates="saved_lists")
    items_list = relationship("Task", back_populates="task_list")

    def __repr__(self):
        return f"<List: {self.name}>"


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    due_date = db.Column(db.String(100), nullable=True)
    is_done = db.Column(db.Boolean, nullable=False)
    is_started = db.Column(db.Boolean, nullable=False)
    position = db.Column(db.Integer, unique=True, nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey("lists.id"))
    task_list = relationship("List", back_populates="items_list")

    def __repr__(self):
        return f"<Task: {self.name}>"


# -------------------- TEMPLATE FILTER FUNCTIONS -------------------- #
@app.template_filter()
def resize_input(value):
    size = len(value)
    if size > 60:
        size = 60
    return size

# Order items
def order_tasks(id_to_list):
    list_to_order = Task.query.filter_by(list_id=id_to_list).all()
    pos = 1
    for task in list_to_order:
        if task.is_started and not task.is_done:
            task.position = pos
            pos += 1
    for task in list_to_order:
        if not task.is_done and not task.is_started:
            task.position = pos
            pos += 1
    for task in list_to_order:
        if task.is_done:
            task.position = pos
            pos += 1
    db.session.commit()

def get_user_lists():
    if not current_user.is_authenticated:
        return []
    data = List.query.filter_by(user_id=current_user.get_id()).all()
    return data

# -------------------- CREATE A NEW LIST AND REDIRECT -------------------- #
@app.route("/", methods=["GET", "POST"])
def new_list():
    register_form, login_form = RegisterUser(), LoginUser()

    if request.method == "POST":
        list_name = f"My To Do List {date.today()}"
        list_url = ShortUUID().random(length=10)
        new_l = List(name=list_name,
                     url=list_url,
                     is_saved=False)
        db.session.add(new_l)
        db.session.commit()

        task = Task(name=request.form.get("new_task"),
                    is_done=False,
                    is_started=False,
                    position=0,
                    list_id=new_l.id)
        db.session.add(task)
        db.session.commit()

        return redirect(url_for("current_list", list_url=list_url))
    return render_template("new_list.html", title="To Do List", login=login_form, register=register_form,
                           current_user=current_user, user_lists=get_user_lists(), this_list=None)


# -------------------- TASK FUNCTIONS (GET, POST, EDIT, DELETE) -------------------- #
# Show all tasks in the list, each list has a unique short url
@app.route("/<list_url>")
def current_list(list_url):
    register_form, login_form = RegisterUser(), LoginUser()

    this_list = List.query.filter_by(url=list_url).first()
    all_tasks = Task.query.filter_by(list_id=this_list.id).order_by(asc(Task.position)).all()

    if this_list.is_saved:
        if not current_user.get_id() == str(this_list.user_id):
            return abort(403)
    return render_template("index.html", title=f"{this_list.name} | To Do List", this_list=this_list, data=all_tasks,
                           register=register_form, login=login_form, current_user=current_user,
                           user_lists=get_user_lists())


# Create a new task in the current list, all values are by default except name of the task
@app.route("/<list_url>/new/<list_id>", methods=["POST"])
def new_task(list_url, list_id):
    new = Task(name=request.form.get("name"),
               is_done=False,
               is_started=False,
               position=0,
               list_id=list_id)
    db.session.add(new)
    db.session.commit()
    order_tasks(list_id)

    return redirect(url_for("current_list", list_url=list_url))


@app.route("/<list_url>/edit/<task_id>", methods=["POST"])
def edit_task(list_url, task_id):
    edit_form = request.form
    item = Task.query.get(task_id)
    item.name = edit_form.get("name")
    item.due_date = edit_form.get("due_date")
    item.is_done = False
    if edit_form.get("is_done") == "on":
        item.is_done = True

    db.session.commit()
    order_tasks(item.list_id)

    return redirect(url_for("current_list", list_url=list_url))


@app.route("/<list_url>/start/<task_id>/<value>")
def start_task(list_url, task_id, value):
    started = Task.query.get(task_id)
    started.is_started = bool(int(value))
    db.session.commit()
    order_tasks(started.list_id)

    return redirect(url_for("current_list", list_url=list_url))


@app.route("/<list_url>/delete-task/<task_id>")
def delete_task(list_url, task_id):
    to_delete = Task.query.get(task_id)
    db.session.delete(to_delete)
    db.session.commit()
    order_tasks(to_delete.list_id)
    return redirect(url_for("current_list", list_url=list_url))


# Save List and user can see it in "My Lists"
@app.route("/<list_url>/save-list")
@login_required
def save_list(list_url):
    to_save = List.query.filter_by(url=list_url).first()
    to_save.is_saved = True
    to_save.user_id = current_user.get_id()

    db.session.commit()
    return redirect(url_for("current_list", list_url=list_url))


# Change List name
@app.route("/<list_url>/change-name/<list_id>", methods=["POST"])
def rename_list(list_url, list_id):
    to_rename = List.query.get(list_id)
    to_rename.name = request.form.get("name")

    db.session.commit()
    return redirect(url_for("current_list", list_url=list_url))


@app.route("/<list_url>/delete-list")
@login_required
def delete_list(list_url):
    to_delete = List.query.filter_by(url=list_url).first()
    for task in Task.query.filter_by(list_id=to_delete.id).all():
        db.session.delete(task)

    db.session.delete(to_delete)
    db.session.commit()
    return redirect(url_for("new_list"))


# -------------------- USER REGISTER AND LOGIN -------------------- #
@app.route("/register", methods=["POST"])
def register():
    data = request.form
    user = User.query.filter_by(email=data.get("email")).first()
    if user:
        flash("This email is already registered.")
    else:
        new_user = User()
        new_user.email = data.get("email")
        new_user.password = generate_password_hash(data.get("password"))

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

    list_url = request.args.get("list_url")
    if list_url is None:
        return redirect(url_for("new_list"))
    return redirect(url_for("current_list", list_url=list_url))


@app.route("/login", methods=["POST"])
def login():
    print(request.args.get("list_url"))
    print(type(request.args.get("list_url")))
    user = User.query.filter_by(email=request.form.get("email")).first()
    if user:
        if check_password_hash(user.password, request.form.get("password")):
            login_user(user)
        else:
            flash("Wrong password.")
    else:
        flash("This email isn't registered.")

    list_url = request.args.get("list_url")
    if list_url is None:
        return redirect(url_for("new_list"))
    return redirect(url_for("current_list", list_url=list_url))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("new_list"))


@app.route("/delete-list-not-saved")
@login_required
@admin_only
def delete_lists():
    lists_to_delete = List.query.filter_by(is_saved=False).all()
    for item in lists_to_delete:
        for task in Task.query.filter_by(list_id=item.id):
            db.session.delete(task)
        db.session.delete(item)
    db.session.commit()
    return "<h1>Listas vacías borradas correctamente</h1>"


if __name__ == '__main__':
    app.run(debug=True)
