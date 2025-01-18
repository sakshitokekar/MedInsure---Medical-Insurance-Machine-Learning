from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from random import randrange
from sqlite3 import *
import pickle

app = Flask(__name__)
app.secret_key="sakshi1234"

app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "medinsure72@gmail.com"
app.config['MAIL_PASSWORD'] = "Med_Insure72"
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

@app.route("/", methods=['GET','POST'])
def home():
	if "username" in session:
		em = session["username"]
		con = None
		uid = 0
		try:
			con = connect('PastInsurancePred.db')
			cursor = con.cursor()
			sql = "select uid from users where emailid = '%s'"
			cursor.execute(sql%(em))
			data = cursor.fetchall()
			for d in data:
				uid = d
			uid = uid[0]
		except Exception as e:
			msg = "Issue" + str(e)
			return render_template("home.html", msg=msg)
		finally:
			if con is not None:
				con.close()

		con = None
		try:
			con = connect('PastInsurancePred.db')
			cursor = con.cursor()
			sql = "select pid,age,sex,bmi,children,smoker,charge from pastpred natural join users where users.uid = '%d'"
			cursor.execute(sql%(uid))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template('home.html', data="No Data Found")
			else:	
				return render_template('home.html', data=data)
			if data is None:
				return render_template('home.html', data="No Data Found")
			else:	
				return render_template('home.html', data=data)
		except Exception as e:
			msg = "No data Found"
			return render_template("home.html", msg=msg)
		finally:
			if con is not None:
				con.close()
	else:
		return redirect(url_for('login'))

@app.route("/logout", methods = ['GET','POST'])
def logout():
	session.pop("username",None)
	return redirect(url_for('login'))


@app.route("/back")
def back():
	return redirect(url_for('home'))

@app.route("/calc", methods = ['GET','POST'])
def calc():
	if "username" in session:
		em = session["username"]
		if request.method == 'POST':
			age = int(request.form["age"])
			sex = request.form["r1"]
			bmi = float(request.form["bmi"])
			children = int(request.form["c"])
			smoker = request.form["s1"]
			if sex == "female":
				gender = 0
			if sex == "male":
				gender = 1
			if smoker == "no":
				smoke = 0
			if smoker == "yes":
				smoke = 1
			d = [[age,gender,bmi,children,smoke]]
			with open("db.model","rb") as f:
				model = pickle.load(f)
			res = float(model.predict(d))
			res = str(round(res,3))
			con = None
			uid = 0
			try:
				con = connect('PastInsurancePred.db')
				cursor = con.cursor()
				sql = "select uid from users where emailid = '%s'"
				cursor.execute(sql%(em))
				data = cursor.fetchall()
				for d in data:
					uid = d
				uid = uid[0]
			except Exception as e:
				msg = "Issue" + str(e)
				return render_template("pred.html", msg=msg)
			finally:
				if con is not None:
					con.close()
			con = None
			try:
				con = connect('PastInsurancePred.db')
				cursor = con.cursor()
				sql = "insert into pastpred (age,bmi,children,sex,smoker,uid,charge) VALUES('%s','%s','%s','%s','%s','%d','%s')"
				cursor.execute(sql%(age,bmi,children,sex,smoker,uid,res))
				con.commit()
			except Exception as e:
				con.rollback()
				msg = "Issue" + str(e)
				return render_template("pred.html", msg=msg)
			finally:
				if con is not None:
					con.close()
				return render_template('pred.html',msg=res)
		else:
			return render_template('pred.html')


@app.route("/signup", methods = ['GET','POST'])
def signup():
	return render_template('signup.html')

@app.route("/emailinput", methods = ['GET','POST'])
def emailinput():
	if request.method == 'POST':
		em = request.form["em"]
		con = None
		try:
			con = connect('PastInsurancePred.db')
			cursor = con.cursor()
			pw = ""
			text="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
			for i in range(8):
				pw = pw + text[randrange(len(text))]
			sql = "insert into users (emailid,pswd) values('%s','%s')"
			cursor.execute(sql%(em,pw))
			con.commit()
			msg = Message("Password for MedInsure",sender="medinsure72@gmail.com", recipients=[em])
			msg.body="Your Password is: " + pw 
			mail.send(msg)
			return render_template('login.html')
		except Exception as e:
			con.rollback()
			return render_template("signup.html",msg="User Already Registered")
		finally:
			if con is not None:
				con.close()
	else:
		return render_template("signup.html")

@app.route("/login", methods = ['GET','POST'])
def login():
	if request.method == 'POST':
		em = request.form['em']
		pw = request.form['pw']
		con = None
		try:
			con = connect("PastInsurancePred.db")
			cursor = con.cursor()
			sql = "select uid from users where emailid = '%s' and pswd='%s'"
			cursor.execute(sql%(em,pw))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template("login.html", msg="Invalid Login")
			else:
				session["username"] = em
				return redirect(url_for('home'))
		except Exception as e:
			msg = "Issue" + str(e)
			return render_template("login.html", msg=msg)
		finally:
			if con is not None:
				con.close()
	else:
		return render_template('login.html')

@app.route("/delentry/<int:pid>")
def delentry(pid):
	con = None
	try:
		con = connect('PastInsurancePred.db')
		cursor = con.cursor()
		sql = "delete from pastpred where pid = '%d'"
		cursor.execute(sql%(pid))
		con.commit()
	except Exception as e:
		con.rollback()
		return render_template("home.html",msg="Deletion Issue")
	finally:
		if con is not None:
			con.close()
		return redirect(url_for('home'))

@app.route("/bmi_calc", methods =["GET", "POST"])
def bmi_calc():
	if request.method == 'POST':
		w = float(request.form.get("weight"))
		h = float(request.form.get("height"))
		bmi_ans = w / (h * h)
		return render_template("BMI.html",bmi_ans=bmi_ans)					
	else:
		return render_template("BMI.html",bmi_ans="Not in POST")					

@app.route("/show_bmi", methods =["GET", "POST"])
def show_bmi():
	return render_template("BMI.html")					

@app.route("/info")
def info():
	return render_template("info.html")

@app.route("/forgot_pswd", methods =["GET", "POST"])
def forgot_pswd():
	if request.method == "POST":
		em = request.form["em"]
		con = None
		try:
			con = connect('PastInsurancePred.db')
			cursor = con.cursor()
			sql = "select * from users where emailid = '%s'"
			cursor.execute(sql%(em))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template("forgot_password.html",msg="User does not exist")
			else:
				pw = ""
				text = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
			for i in range(8):
				pw = pw + text[randrange(len(text))]
			sql = "update users set pswd = '%s' where emailid = '%s'"
			cursor.execute(sql%(pw,em))
			con.commit()
			msg = Message("Password for MedInsure",sender="medinsure72@gmail.com", recipients=[em])
			msg.body="Your New Password is: " + pw 
			mail.send(msg)
			return redirect(url_for('login'))
		except Exception as e:
			con.rollback()
			return render_template("forgot_password.html",msg= str(e))
		finally:
			if con is not None:
				con.close()
	else:
		return render_template("forgot_password.html")		

if __name__ == '__main__':
	app.run(debug = True)