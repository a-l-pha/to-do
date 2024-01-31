from flask import *
from flask_wtf import *
from wtforms import StringField,  SubmitField
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from wtforms.validators import *
from wtforms.widgets import PasswordInput


app = Flask(__name__)
Bootstrap(app)
db = SQLAlchemy(app)

colors = []
mode = 'light'
user = None
email = None
scroll_to = None
message = None
###########
display_mode = ''
'''
# fix phone mode
# when done create light mode
'''

###########

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db.session.expire_on_commit = False


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    is_dark_mode = db.Column(db.Boolean, nullable=False)
    todo_groups = db.relationship('TodoGroup', backref='user', lazy='subquery')


class TodoGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # can enter if you want to
    is_important = db.Column(db.Boolean, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    list_items = db.relationship('ListItem', backref='todo_group', lazy='subquery')


class ListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(250))  # Find way to limit
    description = db.Column(db.String(1000))
    is_important = db.Column(db.Boolean, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('todo_group.id'))
    is_done = db.Column(db.Boolean, nullable=False)


db.create_all()


# Examples


class LoginForm(FlaskForm):
    username = StringField(label='', validators=[DataRequired(), Email()], render_kw={"placeholder": "email"})
    password = StringField(label='', widget=PasswordInput(hide_value=False), validators=[DataRequired(), ],
                           render_kw={"placeholder": "password"})
    submit = SubmitField('Login', )


class SignUpForm(FlaskForm):
    username = StringField(label='', validators=[DataRequired(), Email()], render_kw={"placeholder": "email"})
    password = StringField(label='', widget=PasswordInput(hide_value=False), validators=[DataRequired(), ],
                           render_kw={"placeholder": "password"})
    submit = SubmitField('Sign up')


# First find way to limit characters so sqlite works


@app.route('/')
def home():
    global message
    message = None
    if user:
        a = [group_ for group_ in user.todo_groups if group_.is_important]
        b = [group_ for group_ in user.todo_groups if not group_.is_important]
        user.todo_groups = a + b
        current_group = 0
        for items_ in user.todo_groups:
            c = [group_ for group_ in items_.list_items if group_.is_important]
            d = [group_ for group_ in items_.list_items if not group_.is_important]

            user.todo_groups[current_group].list_items = c + d
            current_group += 1

    return render_template(f'home-{mode}.html', user=user, is_loaded=True)


@app.route('/logout')
def logout():
    global user
    user = None
    return redirect('/')


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    form = SignUpForm(meta={'csrf': False})
    if form.validate_on_submit():
        new_user = User(email=form.username.data, password=form.password.data, is_dark_mode=True, )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')

    return render_template(f'sign-up-{mode}.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    global user, email, message
    form = LoginForm(meta={'csrf': False})
    if form.validate_on_submit():
        print(form.username.data, form.password.data)
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(email=username).first()

        if not user:
            message = 'our database doesnt include you'
            return redirect('/login')

        is_validated = user.password == password

        if user and is_validated:
            # login_user(user)
            email = username

            return redirect('/')

        else:

            message = 'wrong password'
            return redirect('/login')

    return render_template(f'login-{mode}.html', form=form, message=message)


@app.route('/change-mode', methods=['POST', 'GET'])
def toggle_mode():
    global mode
    if mode == 'dark':
        mode = 'light'
    else:
        mode = 'dark'
    return redirect('/')


@app.route('/add-group')
def add_group():
    global user
    if not user:
        return redirect('/sign-up')

    new_todo_group = TodoGroup(title='type here...', is_important=False, user=user)
    db.session.add(new_todo_group)
    print('works')

    new_list_item = ListItem(item='Your item', description='lah blah', is_important=False, todo_group=new_todo_group,
                             is_done=False)
    db.session.add(new_list_item)
    db.session.commit()
    user = User.query.filter_by(email=email).first()

    return redirect(url_for('home'))


@app.route('/delete-group/<int:group_id>')
def delete_group(group_id):
    global user
    group_to_delete = TodoGroup.query.get(group_id)
    db.session.delete(group_to_delete)
    db.session.commit()
    user = User.query.filter_by(email=email).first()
    return redirect('/')


@app.route('/new-title/<int:group_id>', methods=['POST', 'GET'])
def new_title(group_id):
    global user

    group_to_update = TodoGroup.query.get(group_id)
    group_to_update.title = request.form.get('title')
    db.session.add(group_to_update)
    db.session.commit()
    user = User.query.filter_by(email=email).first()
    print(group_to_update.title)

    return redirect('/')


@app.route('/add-point/<int:group_id>', methods=['POST', 'GET'])
def add_point(group_id):
    global user
    group_to_add = TodoGroup.query.get(group_id)
    item = request.form.get('item')
    new_todo_group = ListItem(item=item, is_important=False, description='Something is good about this title',
                              todo_group=group_to_add, is_done=False)
    db.session.add(new_todo_group)
    db.session.commit()
    user = User.query.filter_by(email=email).first()

    return redirect('/')


@app.route('/delete-point/<int:point_id>', )
def delete_point(point_id):
    global user
    point_to_delete = ListItem.query.get(point_id)
    db.session.delete(point_to_delete)
    db.session.commit()
    user = User.query.filter_by(email=email).first()
    return redirect('/')


@app.route('/mark_true/<int:list_id>', methods=['POST', 'GET'])
def mark_true(list_id):
    global user
    list_to_update = ListItem.query.get(list_id)
    list_to_update.is_done = True
    db.session.add(list_to_update)
    db.session.commit()
    user = User.query.filter_by(email=email).first()

    return redirect('/')


@app.route('/mark_false/<int:list_id>', methods=['POST', 'GET'])
def mark_false(list_id):
    global user
    list_to_update = ListItem.query.get(list_id)
    list_to_update.is_done = False
    db.session.add(list_to_update)
    db.session.commit()
    user = User.query.filter_by(email=email).first()

    return redirect('/')


@app.route('/toggle_importance/<int:list_id>', methods=['POST', 'GET'])
def toggle_imp(list_id):
    global user
    list_to_update = ListItem.query.get(list_id)
    if list_to_update.is_important:
        list_to_update.is_important = False
    elif not list_to_update.is_important:
        list_to_update.is_important = True

    db.session.add(list_to_update)

    db.session.commit()
    user = User.query.filter_by(email=email).first()

    # sort by importance

    return redirect('/')


@app.route('/toggle_importance_group/<int:group_id>', methods=['POST', 'GET'])
def toggle_imp_group(group_id):
    global user
    group_to_update = TodoGroup.query.get(group_id)
    if group_to_update.is_important:
        group_to_update.is_important = False
    elif not group_to_update.is_important:
        group_to_update.is_important = True

    db.session.add(group_to_update)
    db.session.commit()
    user = User.query.filter_by(email=email).first()

    return redirect('/')


@app.route('/new-description/<int:list_id>', methods=['POST', 'GET'])
def new_description(list_id):
    global user

    list_to_update = ListItem.query.get(list_id)
    list_to_update.description = request.form.get('item')
    db.session.add(list_to_update)
    db.session.commit()
    user = User.query.filter_by(email=email).first()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
