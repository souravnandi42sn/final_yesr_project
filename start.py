from flask import Flask,flash,redirect,url_for,session,logging,request,jsonify
from flask import render_template
from database import Articles
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,DateField
from passlib.hash import sha256_crypt
import cx_Oracle
from functools import wraps
import os
import requests
from bs4 import BeautifulSoup
from database import preprocessing
from gather_data import return_values
from random import sample

app=Flask(__name__)

Article=Articles()

app.debug=True

#sabhi news ko lene ke lia home page mein hinsdustan times ka rss liya gaya h

@app.route('/home')
def index():
    url = "http://www.hindustantimes.com/rss/topnews/rssfeed.xml"

    resp = requests.get(url)

    soup = BeautifulSoup(resp.content, features="xml")

    items = soup.findAll('item')

    news_items = []

    for item in items:
        news_item = {}
        news_item['title'] = item.title.text
        news_item['description'] = item.description.text
        news_item['link'] = item.link.text
        news_item['image'] = item.content['url']
        news_items.append(news_item)
    return render_template("home.html",news_items=news_items)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/articles')
def articles():
    return render_template("articles.html",articles=Article)#here with article parameter we are passingh the data

@app.route('/question/<string:id>')
def article(id):
    con = cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
    cur = con.cursor()
    cur.execute('select * from questions where qid = :id', {"id": id})
    res = cur.fetchall()
    dict = {}
    qtns = []
    for i in res:
        dict["id"] = i[0]
        dict["title"] = i[1]
        dict["body"] = i[2][3:len(i[2]) - 3]
        dict["authorid"] = i[3]
        cur.execute('select name from webusers where id=:id', {"id": i[3]})
        dict["name"] = cur.fetchall()[0][0]
        dict["create_date"] = i[4].date()
        qtns.append(dict)
        #qtns is the list of questions with its details(questionid,body,authorid) kept in dictionary for each question

    return render_template("question.html",questions=qtns)

class TransactionForm(Form):
    fromCity=StringField('fromCity',[validators.required()])
    toCity=StringField('toCity',[validators.required()])
    datef=DateField('datef', format='%m/%d/%Y')



class RegisterForm(Form):
    name=StringField('Name',[validators.required(),validators.length(min=1,max=50)])
    username=StringField('UserName',[validators.required(),validators.length(min=4,max=25)])
    email=StringField('Email',[validators.optional(),validators.length(min=6,max=50)])
    password=PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm',message='password do not match'),
        validators.length(min=6)
    ])
    confirm=PasswordField('Confirm Password',[validators.required()])

@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(str(form.password.data))#password is encyped with hashing function

        #now add the registering data to  the database
        con=cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
        cur = con.cursor()
        cur.execute('insert into webusers(id,name,email,username,password) values(id.nextval,:1,:2,:3,:4)',(name,email,username,password))
        con.commit()
        con.close()

        flash('you are successfully registered and can log in','success')

        return redirect(url_for('index'))#yahan par function name dena h jis url pe jana chahtein h.

    return render_template('register.html',form=form)

#for login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password_got=request.form['password']

        con = cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
        cur = con.cursor()
        cur.execute('select password,name,id from webusers where username=:userna',{"userna":username})
        res = cur.fetchall()
        p = {}
        if(len(res)>0):
            for i in res:
                p[i[2]] =[i[0],i[1]] #yahan par i[0] password h aur i[1] uska related "name" jo ki "res" se lia gaya h
            pas=0
            for i in p:
                if sha256_crypt.verify(password_got,p[i][0]):
                    session['logged_in']=True
                    session['name']=p[i][1]
                    session['id']=i

                    flash('you are logged in','success')
                    return redirect(url_for('dashboard'))#yahan par dashboard function ko bula rahe h...
                    pas=pas+1
                    break
            if(pas!=1):
                error = "Wrong Password"
                render_template('login.html', error=error)

        else:
            error="No username Found"
            render_template('login.html',error=error)
    return render_template('login.html')

#dashBoard ko restrict karne ke lia ki wo direct link search karne se aa nah jae...agar logged in ho tabhi aaye
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized,Please Login','danger')
            return redirect(url_for('login'))
    return wrap



@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('you are logged out','success')
    return redirect(url_for('login'))

@app.route('/dashi')
@is_logged_in
def dashi():
    flipcarts,flipcart_predicts,amazons,amazon_predicts,per,fl_rate,fl_per,amazon_rating_averages,flipcart_most_buyed_prduct_details=return_values()
    return render_template("start.html",flipcarts=flipcarts,flipcart_predicts=flipcart_predicts,amazons=amazons,amazon_predicts=amazon_predicts,per=per,fl_rate=fl_rate,fl_per=fl_per,amazon_rating_averages=amazon_rating_averages,flipcart_most_buyed_prduct_details=flipcart_most_buyed_prduct_details)


#dashboard
@app.route('/dashboard')
@is_logged_in#yeh wo uppar wale restriction function ko bula leta h,jo kdashBoard ko restrict karne ke lia ki wo direct link search karne se aa nah jae...agar logged in ho tabhi aayei
def dashboard():
    con = cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
    cur = con.cursor()
    cur.execute('select * from questions where authorid = :id',{"id":session["id"]})
    res=cur.fetchall()
    dict = {}
    qtns = []
    for i in res:
        dict["id"] = i[0]
        dict["title"] = i[1]
        dict["body"] = i[2][3:len(i[2]) - 3]
        dict["authorid"] = i[3]
        cur.execute('select name from webusers where id=:id', {"id": i[3]})
        dict["name"] = cur.fetchall()[0][0]
        dict["create_date"] = i[4].date()
        qtns.append(dict)

    if len(qtns)>0:
        return render_template('dashboard.html',questions=qtns)#abb yeh jo "questions" variavble mein "qtns assign kar rahe h wo by using "questions" variable we can access in dashboard.html"
    else:
        message="No articles found"
        return render_template('dashboard.html',msg=message)# if there is no such articles then just show the "dashboard" empty with message
    cur.close()




#article input form
class ArticleForm(Form):
    title=StringField('Title',[validators.required(),validators.length(min=1,max=200)])
    body=TextAreaField('Body',[validators.required(),validators.length(min=30)])

#add_article route link is made here
@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
    form=ArticleForm(request.form)
    if request.method=='POST' and form.validate(): #if the input criterias are all validated and the method is POST that means we are allocating some values
        title=form.title.data#if valid data is taken then take it into "form" and "body" variables
        body=form.body.data

        # now add the title and the question/Article to the "Quetions" table
        con = cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
        cur = con.cursor()
        cur.execute('insert into questions(qid,title,body,authorid) values(id.nextval,:1,:2,:3)',(title,body,session['id']))
        con.commit()
        con.close()
        flash('Article created','success')

        return redirect(url_for('dashboard'))
    return  render_template('add_article.html',form=form)#before we check for the POST and validation we need to render the template to the "add_Article" for getting the entries which we want to validate

@app.route('/edit_question/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_question(id):
    # now edit the title and the question/Article to the "Quetions" table
    con = cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
    cur = con.cursor()

    cur.execute('select title,body  from questions where qid=:id', {"id": id})
    res2 = cur.fetchall()
    print(res2)
    dict2 = {}
    qtns2 = []
    for i in res2:
        dict2["title"] = i[0]
        dict2["body"] = i[1][3:len(i[1]) - 4]
        qtns2.append(dict2)
    print(qtns2)

    #yahan par apan ne  ekk structure bana lia h to display the written data
    form = ArticleForm(request.form)
    #abb uss dachein mein data dalo...
    form.title.data=qtns2[0]["title"]
    form.body.data=qtns2[0]["body"]

    if request.method == 'POST' and form.validate():  # if the input criterias are all validated and the method is POST that means we are allocating some values
        title =request.form['title'] # if valid data is taken then take it into "form" and "body" variables
        body =request.form['body']

        # now add the title and the question/Article to the "Quetions" table
        con = cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
        cur = con.cursor()

        cur.execute('update questions set title=:title,body=:body where qid=:id',{"title":title,"id":id,"body":body})
        con.commit()
        con.close()
        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_question.html', form=form)

#jo har ekk question ko delete karne ke lia chahia yeh wo route h
@app.route('/delete_question/<string:id>',methods=['GET','POST'])#koi bhi action from the "form" context karne ke lia routh method mangta h ,matlab yauss form se data lena h(POST) ya display karna h(GET)
@is_logged_in
def delete_question(id):
    con = cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
    cur = con.cursor()

    cur.execute('delete from questions where qid=:id',{"id":id})
    con.commit()
    con.close()
    flash('deleted question','success')
    return redirect(url_for('dashboard'))




@app.route('/profile')
@is_logged_in
def profile():
    return render_template('profile.html')

#yeh current working directory ka pura path deh dega
#yeh bellow line yeh path dega:C:\Users\sourav nandi\PycharmProjects\first\flask
App_route=os.path.dirname(os.path.abspath(__file__))


@app.route('/upload',methods=["GET","POST"])
@is_logged_in
def upload():
    """#know in this current path in App_route we need to add the file_name where the image is present
    target=os.path.join(App_route,"images/")
    print("target:",target)
    if not os.path.isdir(target):#agar director images ki iss path mein nah present ho toh then make that directory
        os.mkdir(target)
    for file in request.files.getlist("file"):
        print("file:",file)
        filename=file.filename #this returns the file_name
        print("filename:",filename)
    return  render_template("dashboard.html")
    """
    con = cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
    cur = con.cursor()
    for file in request.file.getList("file"):
            cur.execute('insert into images values(file:,id:)', {"file": file,"id":session[id]})
            flash("inserted the image to the table","succuess")
    return render_template("dashboard.html")





import pandas as pd

@app.route("/upload_file",methods=["POST"])
def uploade_file():
	file=request.files['myfile']
    # for checking that the input file is a csv file
	if ( file.filename.endswith('.csv')):
		dataset=pd.read_csv(file)
		datalist=preprocessing(dataset)
		print("jsonify",jsonify(datalist))
	return render_template("graphs.html",datalist=jsonify(datalist))

@app.route("/data")
def data():
    d={}
    d['y']=1
    return jsonify(d)

@app.route('/test')
def test():
    return render_template("test.html")

qtns=[]

@app.route("/flights",methods=['POST','GET'])
@is_logged_in
def flights():
    form = TransactionForm(request.form)
    if request.method == 'POST' and form.validate():
        qtns.clear()
        fromf=form.fromCity.data
        tof=form.toCity.data
        datef=form.datef.data
        con = cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
        cur = con.cursor()
        cur.execute("select fromCity,toCity,costf,timef,flight_id from flights where fromCity='kolkata' and tocity='mumbai'")
        #cur.execute('select fromCity,toCity,costf,timef from flights where fromCity=:1 and tocity=:2 ',{str(fromf),str(tof)})
        #cur.execute('insert into webusers(TRID,USERID,DT,FROMCITY,TOCITY,TfromCityOTALCOST) values(TRID.nextval,:1,:2,:3,:4,500)',session["id"],datef,fromf,tof))
        res = cur.fetchall()
        print(res)
        dict = {}
        for i in res:
            dict["fromcity"] = i[0]
            dict["tocity"] = i[1]
            dict["cost"]=i[2]
            dict["timef"]=i[3]
            dict["flight_id"]=i[4]
            qtns.append(dict)
        con.commit()
        con.close()

        flash('you are successfully registered and can log in','success')

        return redirect(url_for("flights_p"))
    return render_template("flights.html",form=form)

@app.route('/flights_p')
def flights_p():
    print("qtns",qtns)
    return render_template('flights_p.html',qtns=qtns)

@app.route("/book")
def book():
    con = cx_Oracle.connect\
        ('system/$Sn8987480720@127.0.0.1/orcl')
    cur = con.cursor()
    cur.execute('select fromCity,toCity,costf,timef,flight_id from flights where flight_id=:id', {"id": my_var})
    print(cur.fetchall())
    return render_template("book.html")


if __name__=="__main__":
    app.secret_key='sourav123'
    app.run()
#article ka database ka "reply" field in a list kaise save kare