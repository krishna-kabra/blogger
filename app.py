from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime

with open("E:/web learning/Flask/blogging/config.json","r") as c:
    params = json.load(c)['params']


app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['email'],
    MAIL_PASSWORD=  params['epassword']
)
mail = Mail(app)

class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subtitle = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(20), nullable=False)



@app.route("/")
def index():
    post = posts.query.all()
    return render_template("index.html",post=post)



@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/post/<string:slug>")
def post(slug):
    post = posts.query.filter_by(slug=slug).first()
    return render_template("post.html",post=post,slug=slug)

@app.route("/post")
def post_fetch():
    post = posts.query.all()
    return render_template("post_fetch.html",post=post)



@app.route("/login",methods=['GET','POST'])
def login():
    if "user" in session and session['user']==params['uname']:
        post = posts.query.all()
        return render_template("dashboard.html", params=params,post=post)

    if request.method == "POST":
        uname = request.form.get('name')
        password = request.form.get('password')
        if uname == params["uname"] and password == params['password']:
            session['user']=uname
            post = posts.query.all()
            return render_template("dashboard.html",post=post)
        else:
            return "your user name and password should wrong"
    else:
        return render_template("login.html",params=params)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if "user" in session and session['user'] == params['uname']:
        if request.method == "POST":
            title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            slug = request.form.get('slug')
            content = request.form.get('content')
            image = request.form.get('image')
            date = datetime.now()
            if sno == '0':
                post = posts(title=title, slug=slug, content=content, subtitle=subtitle, image=image, date=date)
                db.session.add(post)
                db.session.commit()
                return redirect("/login")
            else:
                post = posts.query.filter_by(sno=sno).first()
                post.title = title
                post.subtitle = subtitle
                post.slug = slug
                post.content = content
                post.image = image
                post.date = date
                db.session.commit()
                return redirect('/login')

        post = posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post,sno=sno)
    return render_template('login.html', params=params)

@app.route("/contact",methods =['GET','POST'])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        add = Contacts(name=name,email=email,phone=phone,message=message,date =datetime.now())
        db.session.add(add)
        db.session.commit()
    return render_template("contact.html",params=params)
    mail.send_message("New message from :- "+name,
    sender = email,
    recipients=params['gmail'],
    body=message + "\n" + phone
    )

@app.route("/delete/<string:sno>")
def delete(sno):
    a = posts.query.get(sno)
    db.session.delete(a)
    db.session.commit()
    return redirect('/login')

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)