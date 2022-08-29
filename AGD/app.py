from flask import Flask, render_template, request, Response, url_for, redirect
from sqlite3 import * 
from camera import Video

app=Flask(__name__, static_url_path="", static_folder="templates")

@app.route("/")
def home():
	return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
	if request.method == "POST":	
		name = request.form["name"]
		location = request.form["location"]
		zodiac = request.form["zodiac"]
		interests = request.form["interests"]
		con=None
		try:
			con=connect("register.db")
			cursor=con.cursor()
			sql = "insert into users values('%s', '%s', '%s', '%s')"
			cursor.execute(sql %(name, location, zodiac, interests))
			con.commit()
			return redirect(url_for("agendetect"))
		except Exception as e:
			con.rollback()
			return render_template("signup.html")
		finally:
			if con is not None:
				con.close()
	else:
		return render_template("signup.html")

@app.route("/agendetect")
def agendetect():
	return render_template("agendetect.html")

def gen(camera):
	while True:
		frame=camera.get_frame()
		yield(b'--frame\r\n'
       b'Content-Type:  image/jpeg\r\n\r\n' + frame +
         b'\r\n\r\n')

	return redirect( url_for("user"))	 
		
@app.route("/video")
def video():
	return Response(gen(Video()),
	mimetype='multipart/x-mixed-replace; boundary=frame')
	
@app.route("/user")
def user():
	con=None
	try:
		con=connect("register.db")
		cursor=con.cursor()
		sql= "select * from users"
		cursor.execute(sql)
		data=cursor.fetchall()
		return render_template("user.html", msg=data)
	except Exception as e:
		return render_template("user.html", msg=e)
	finally:
		if con is not None:
			con.close()

	return render_template("home.html")
	
if __name__ == "__main__":
	app.run(debug=True, use_reloader=True)
