from flask import Flask
from flask import Blueprint
from academy_login_section import academy_signin
from academy_course_section import academy_course_details


app = Flask(__name__)
app.register_blueprint(academy_signin, url_prefix='/academy_login_section')
app.register_blueprint(academy_course_details, url_prefix='/academy_course_section')

@app.route('/')
def index():
	return 'Hello World'

if __name__ == '__main__':
	#app.run()
	app.run(host='0.0.0.0',debug=True)
