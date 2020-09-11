import pymysql
from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
from database_connections import creamson_academy_connection
from werkzeug import secure_filename
from awsconfig import ACCESS_KEY,SECRET_KEY
import boto3
import os

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
academy_course_details = Blueprint('academy_course_details_api', __name__)
api = Api(academy_course_details,  title='MyElsa Academy API',description='MyElsa Academy API')
name_space = api.namespace('academyCourseDetails',description='Academy Course Details')

BASE_URL = 'https://my-loadbalancer-1932033183.us-east-2.elb.amazonaws.com/flaskapp/'


@academy_course_details.route('/getUserEnrolledCourses/<int:user_id>',methods=['GET'])
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])
def getUserEnrolledCourses(user_id):
	connection = creamson_academy_connection()
	cursor = connection.cursor()

	cursor.execute("""SELECT `course_id`,`course_name`,`course_desc`,`course_image`,`duration_in_days`,
		`duration_in_weeks`,`duration_in_hours`,`no_of_modules`,`no_of_workshops`,`no_of_assessments`,
		`no_of_sessions` FROM `course` WHERE `course_id` in (SELECT `course_id` 
		FROM `user_course_mapping` WHERE `user_id` = %s)""",(user_id))

	courseDtls = cursor.fetchall()
	# response = jsonify({"attributes": {"status_desc": "User Enrolled Course List",
	# 							"status": "success"},
	# 			"responseList":courseDtls})
	# response.headers.add('Access-Control-Allow-Origin', '*')
	return jsonify({"attributes": {"status_desc": "User Enrolled Course List",
								"status": "success"},
				"responseList":courseDtls})


@name_space.route("/getUserEnrolledCourses/<int:user_id>")
class getUserEnrolledCourses(Resource):
	@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])
	def get(self,user_id):

		connection = creamson_academy_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `course_id`,`course_name`,`course_desc`,`course_image`,`duration_in_days`,
			`duration_in_weeks`,`duration_in_hours`,`no_of_modules`,`no_of_workshops`,`no_of_assessments`,
			`no_of_sessions` FROM `course` WHERE `course_id` in (SELECT `course_id` 
			FROM `user_course_mapping` WHERE `user_id` = %s)""",(user_id))

		courseDtls = cursor.fetchall()

		# courseDtls = [{'course_id':1,
		# 				'course_name':'Teacher Training'}]

		return ({"attributes": {"status_desc": "User Enrolled Course List",
								"status": "success"},
				"responseList":courseDtls})

		# return courseDtls


@academy_course_details.route('/getProgramListByCourseId/<int:user_id>/<int:course_id>')
@cross_origin(origin='*')
def getProgramListByCourseId(user_id,course_id):
	connection = creamson_academy_connection()
	cursor = connection.cursor()

	cursor.execute("""SELECT ucm.`course_id`,`course_name` FROM `user_course_mapping` ucm, 
		`course` co WHERE `user_id` = %s and ucm.`course_id` = %s""",(user_id,course_id))

	subCourse = cursor.fetchone()
	msg = 'not-found'
	course_name = None
	moduleDtls = []
	if subCourse:

		cursor.execute("""SELECT cmm.`module_id`,`module_squence_id` as 'sequence_id',`module_name`,
			`module_desc` as 'module_description',`module_type_name` as 'module_type',module_no
			FROM `course_module_mapping` cmm INNER JOIN `module` mo on cmm.`module_id` = mo.`module_id` 
			INNER JOIN `module_type` mt on mo.`module_type_id` = mt.`module_type_id` 
			WHERE `course_id` = 1""")

		moduleDtls = cursor.fetchall()
		msg = 'found'
		course_name = subCourse.get('course_name')
		
	return ({"attributes": {"status_desc": "Module List",
							"status": "success",
							"course_name":course_name,
							"msg":msg},
			"responseList":moduleDtls})

@name_space.route("/getProgramListByCourseId/<int:user_id>/<int:course_id>")
class getProgramListByCourseId(Resource):
	def get(self,user_id,course_id):

		connection = creamson_academy_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT ucm.`course_id`,`course_name` FROM `user_course_mapping` ucm, 
			`course` co WHERE `user_id` = %s and ucm.`course_id` = %s""",(user_id,course_id))

		subCourse = cursor.fetchone()
		msg = 'not-found'
		course_name = None
		moduleDtls = []
		if subCourse:

			cursor.execute("""SELECT cmm.`module_id`,`module_squence_id` as 'sequence_id',`module_name`,
				`module_desc` as 'module_description',`module_type_name` as 'module_type',module_no
				FROM `course_module_mapping` cmm INNER JOIN `module` mo on cmm.`module_id` = mo.`module_id` 
				INNER JOIN `module_type` mt on mo.`module_type_id` = mt.`module_type_id` 
				WHERE `course_id` = 1""")

			moduleDtls = cursor.fetchall()
			msg = 'found'
			course_name = subCourse.get('course_name')
			# moduleDtls = [{'module_id':1,
			# 				'module_type':'Module',
			# 				'module_name':'Teacher Training 1',
			# 				'module_no':'Module 1',
			# 				'module_description':'',
			# 				'sequence_id':1
			# 				},
			# 				{'module_id':2,
			# 				'module_type':'Module',
			# 				'module_name':'Teacher Training 2',
			# 				'module_no':'Module 2',
			# 				'module_description':'',
			# 				'sequence_id':2
			# 				},
			# 				{'module_id':3,
			# 				'module_type':'Module',
			# 				'module_name':'Teacher Training 3',
			# 				'module_no':'Module 3',
			# 				'module_description':'',
			# 				'sequence_id':3
			# 				},
			# 				{'module_id':4,
			# 				'module_type':'Case Study',
			# 				'module_name':'Teacher Training 3',
			# 				'module_no':'Case Study 1',
			# 				'module_description':'',
			# 				'sequence_id':4
			# 				}]

		return ({"attributes": {"status_desc": "Module List",
								"status": "success",
								"course_name":course_name,
								"msg":msg},
				"responseList":moduleDtls})


@academy_course_details.route('/getSessionListByModuleId/<int:user_id>/<int:module_id>')
@cross_origin(origin='*')
def getSessionListByModuleId(user_id,module_id):

	connection = creamson_academy_connection()
	cursor = connection.cursor()
	course_id = 1
	cursor.execute("""SELECT ucm.`course_id`,`course_name` FROM `user_course_mapping` ucm, 
		`course` co WHERE `user_id` = %s and ucm.`course_id` = %s""",(user_id,course_id))

	subCourse = cursor.fetchone()
	msg = 'not-found'
	course_name = None
	sessionDtls = []
	if subCourse:
		cursor.execute("""SELECT msm.`session_id`,`session_name`,`session_desc` as 'session_description',
			`duration_in_hours`, `session_sequence_id` as 'sequence_id', 
			concat('Session ',`session_sequence_id`) as 'session_no' 
			FROM `module_session_mapping` msm inner JOIN `session` ss 
			on msm.`session_id` = ss.`session_id` WHERE `module_id` = %s 
			order by `session_sequence_id`""",(module_id))

		sessionDtls = cursor.fetchall()
		msg = 'found'
		course_name = subCourse.get('course_name')

		for sid, sess in enumerate(sessionDtls):
			cursor.execute("""SELECT ssm.`segment_id`,`segment_name`,`segment_desc`,
				`duration_in_seconds`*60 as 'duration_in_minutes',`weightage`,`segment_sequence_id` FROM 
				`session_segment_mapping` ssm INNER JOIN `segment` sg 
				on ssm.`segment_id` = sg.`segment_id` WHERE `session_id` = %s 
				order by `segment_sequence_id`""",(sess.get('session_id')))

			segDtls = cursor.fetchall()
			sess['segmentDtls'] = segDtls

		# sessionDtls = [{'session_id':1,
		# 				'session_name':'Teacher Training 1',
		# 				'session_no':'Session 1',
		# 				'session_description':'',
		# 				'sequence_id':1,
		# 				'segmentDtls':[{'segment_id':1,
		# 								'segment_name':'Teacher Training 1',
		# 								'sequence_id':1}]
		# 				}]

	return ({"attributes": {"status_desc": "Session List",
							"status": "success",
							"course_name":course_name,
							"msg":msg},
			"responseList":sessionDtls})

@name_space.route("/getSessionListByModuleId/<int:user_id>/<int:module_id>")
class getSessionListByModuleId(Resource):
	def get(self,user_id,module_id):

		connection = creamson_academy_connection()
		cursor = connection.cursor()
		course_id = 1
		cursor.execute("""SELECT ucm.`course_id`,`course_name` FROM `user_course_mapping` ucm, 
			`course` co WHERE `user_id` = %s and ucm.`course_id` = %s""",(user_id,course_id))

		subCourse = cursor.fetchone()
		msg = 'not-found'
		course_name = None
		sessionDtls = []
		if subCourse:
			cursor.execute("""SELECT msm.`session_id`,`session_name`,`session_desc` as 'session_description',
				`duration_in_hours`, `session_sequence_id` as 'sequence_id', 
				concat('Session ',`session_sequence_id`) as 'session_no' 
				FROM `module_session_mapping` msm inner JOIN `session` ss 
				on msm.`session_id` = ss.`session_id` WHERE `module_id` = %s 
				order by `session_sequence_id`""",(module_id))

			sessionDtls = cursor.fetchall()
			msg = 'found'
			course_name = subCourse.get('course_name')

			for sid, sess in enumerate(sessionDtls):
				cursor.execute("""SELECT ssm.`segment_id`,`segment_name`,`segment_desc`,
					`duration_in_seconds`*60 as 'duration_in_minutes',`weightage`,`segment_sequence_id` FROM 
					`session_segment_mapping` ssm INNER JOIN `segment` sg 
					on ssm.`segment_id` = sg.`segment_id` WHERE `session_id` = %s 
					order by `segment_sequence_id`""",(sess.get('session_id')))

				segDtls = cursor.fetchall()
				sess['segmentDtls'] = segDtls

		return ({"attributes": {"status_desc": "Session List",
								"status": "success",
								"course_name":course_name,
								"msg":msg},
				"responseList":sessionDtls})


@name_space.route("/getSegmentDtlsBySegmentId/<int:user_id>/<int:segment_id>/<int:course_id>")
class getSessionListByModuleId(Resource):
	def get(self,user_id,segment_id,course_id):

		connection = creamson_academy_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT ucm.`course_id`,`course_name` FROM `user_course_mapping` ucm, 
			`course` co WHERE `user_id` = %s and ucm.`course_id` = %s""",(user_id,course_id))

		subCourse = cursor.fetchone()
		msg = 'not-found'
		course_name = None
		segmentDtls = []
		if subCourse:

			cursor.execute("""SELECT `content_type_id`,`text_resource_id`,`sequence_id` FROM `segment_content_mapping` 
				WHERE `segment_id` = %s order by `sequence_id`""",(segment_id))

			segmentDtls = cursor.fetchall()
			msg = 'found'
			course_name = subCourse.get('course_name')

			for sid, seg in enumerate(segmentDtls):
				contentType = None
				if seg.get('content_type_id') == 2:
					cursor.execute("""SELECT `resource_name`,`resource_url`,`resource_type` 
						FROM `segment_resource_content` WHERE `resource_id` = %s""",(seg.get('text_resource_id')))

					contentDtls = cursor.fetchone()
					seg['contentType'] = 'resource'
					if contentDtls:
						seg['resource_name'] = contentDtls.get('resource_name')
						seg['resource_url'] = contentDtls.get('resource_url')
						seg['resource_type'] = contentDtls.get('resource_type')

				elif seg.get('content_type_id') == 1:
					cursor.execute("""SELECT `text_content_name`,`text_content`,`html_text_content` 
						FROM `segment_text_content` WHERE `text_content_id` = %s""",(seg.get('text_resource_id')))
						
					contentDtls = cursor.fetchone()
					seg['contentType'] = 'text'
					if contentDtls:
						seg['text_content_name'] = contentDtls.get('text_content_name')
						seg['text_content'] = contentDtls.get('text_content')#.replace('\r\n',' ')
						seg['html_text_content'] = contentDtls.get('html_text_content')
				else:
					pass

		return ({"attributes": {"status_desc": "Segment Details",
								"status": "success",
								"course_name":course_name,
								"msg":msg},
				"responseList":segmentDtls})



@academy_course_details.route("/getSegmentDtlsBySegmentId/<int:user_id>/<int:segment_id>/<int:course_id>")
@cross_origin(origin='*')
def getSegmentDtlsBySegmentId(user_id,segment_id,course_id):

	connection = creamson_academy_connection()
	cursor = connection.cursor()

	cursor.execute("""SELECT ucm.`course_id`,`course_name` FROM `user_course_mapping` ucm, 
		`course` co WHERE `user_id` = %s and ucm.`course_id` = %s""",(user_id,course_id))

	subCourse = cursor.fetchone()
	msg = 'not-found'
	course_name = None
	segmentDtls = []
	if subCourse:

		cursor.execute("""SELECT `content_type_id`,`text_resource_id`,`sequence_id` FROM `segment_content_mapping` 
			WHERE `segment_id` = %s order by `sequence_id`""",(segment_id))

		segmentDtls = cursor.fetchall()
		msg = 'found'
		course_name = subCourse.get('course_name')

		for sid, seg in enumerate(segmentDtls):
			contentType = None
			if seg.get('content_type_id') == 2:
				cursor.execute("""SELECT `resource_name`,`resource_url`,`resource_type` 
					FROM `segment_resource_content` WHERE `resource_id` = %s""",(seg.get('text_resource_id')))

				contentDtls = cursor.fetchone()
				seg['contentType'] = 'resource'
				if contentDtls:
					seg['resource_name'] = contentDtls.get('resource_name')
					seg['resource_url'] = contentDtls.get('resource_url')
					seg['resource_type'] = contentDtls.get('resource_type')

			elif seg.get('content_type_id') == 1:
				cursor.execute("""SELECT `text_content_name`,`text_content`,`html_text_content` 
					FROM `segment_text_content` WHERE `text_content_id` = %s""",(seg.get('text_resource_id')))
					
				contentDtls = cursor.fetchone()
				seg['contentType'] = 'text'
				if contentDtls:
					seg['text_content_name'] = contentDtls.get('text_content_name')
					seg['text_content'] = contentDtls.get('text_content')#.replace('\r\n',' ')
					seg['html_text_content'] = contentDtls.get('html_text_content')
			elif seg.get('content_type_id') == 3:
				seg['contentType'] = 'quiz'
				getUserAssessmentURL = BASE_URL + 'academy_course_section/getQuestionsByAssessmentId/{}'.format(seg.get('text_resource_id'))

				assessmentDtls = requests.get(getUserAssessmentURL,verify=False).json().get('responseList')
				cursor.execute("""SELECT `status`,`marks` FROM `user_assessment_status_mapping` 
					WHERE `user_id` = %s and `assessment_id` = %s""",(user_id,seg.get('text_resource_id')))

				userAssmStatus = cursor.fetchone()

				if userAssmStatus:
					assmStatus = userAssmStatus.get('status')
					for aid, assm in enumerate(assessmentDtls):
						cursor.execute("""SELECT `Option_ID`,`Answer`,`answersheet_filepath`,`filetype`,
						 	`marks`,answer_flag FROM `student_answers` WHERE `Assessment_ID` = %s
						 	and `user_id` = %s and `Question_ID` =  %s order by date(`Last_Update_TS`) 
						 	desc limit 1""",(seg.get('text_resource_id'),user_id,assm.get('Question_ID')))

						usrAnswer = cursor.fetchall()
						if usrAnswer:
							assm['userAnswers'] = usrAnswer
						else:
							assm['userAnswers'] = []
				else:
					assmStatus = 'incomplete'
				seg['userAssessmentStatus'] = assmStatus
				seg['quizDtls'] = assessmentDtls
			else:
				pass

	return ({"attributes": {"status_desc": "Segment Details",
							"status": "success",
							"course_name":course_name,
							"msg":msg},
			"responseList":segmentDtls})


@academy_course_details.route("/getWorkshopListByModuleId/<int:user_id>/<int:module_id>/<int:course_id>")
@cross_origin(origin='*')
def getWorkshopListByModuleId(user_id,module_id,course_id):
	connection = creamson_academy_connection()
	cursor = connection.cursor()

	cursor.execute("""SELECT ucm.`course_id`,`course_name` FROM `user_course_mapping` ucm, 
		`course` co WHERE `user_id` = %s and ucm.`course_id` = %s""",(user_id,course_id))

	subCourse = cursor.fetchone()
	msg = 'not-found'
	course_name = None
	workshopDtls = []
	if subCourse:
		cursor.execute("""SELECT mwm.`workshop_id`,`workshop_name`,`workshop_desc`,`workshop_startdate`,
			workshop_enddate,`workshop_url` FROM `module_workshop_mapping` mwm INNER JOIN `workshop` wk 
			on mwm.`workshop_id` = wk.`workshop_id` WHERE `module_id` = %s""",(module_id))

		workshopDtls = cursor.fetchall()
		msg = 'found'
		course_name = subCourse.get('course_name')
		for wid, work in enumerate(workshopDtls):
			work['workshop_startdate'] = work.get('workshop_startdate').isoformat()
			work['workshop_enddate'] = work.get('workshop_enddate').isoformat()


	return jsonify({"attributes": {"status_desc": "Workshop List",
									"status": "success",
									"course_name":course_name,
									"msg":msg},
					"responseList":workshopDtls})


@academy_course_details.route("/getAssessmentByModuleId/<int:user_id>/<int:module_id>/<int:course_id>")
@cross_origin(origin='*')
def getAssessmentByModuleId(user_id,module_id,course_id):

	connection = creamson_academy_connection()
	cursor = connection.cursor()
	cursor.execute("""SELECT ucm.`course_id`,`course_name` FROM `user_course_mapping` ucm, 
		`course` co WHERE `user_id` = %s and ucm.`course_id` = %s""",(user_id,course_id))

	subCourse = cursor.fetchone()
	msg = 'not-found'
	course_name = None
	assessmentDtls = []
	if subCourse:

		cursor.execute("""SELECT mam.`assessment_id`,`assessment_name`,`assessment_desc`,
			`assessment_filepath`,`filetype`,`due_date` FROM `module_assessment_mapping` mam 
			INNER JOIN `assessment` ass on mam.`assessment_id` = ass.`assessment_id` 
			WHERE mam.`module_id` = %s""",(module_id))

		assessmentDtls = cursor.fetchall()
		msg = 'found'
		course_name = subCourse.get('course_name')
		for aid, assm in enumerate(assessmentDtls):
			assm['due_date'] = assm.get('due_date').isoformat()

	return ({"attributes": {"status_desc": "Workshop List",
							"status": "success",
							"course_name":course_name,
							"msg":msg},
			"responseList":assessmentDtls})


@academy_course_details.route("/uploadToS3Bucket/<string:user_id>",methods=['POST'])
@cross_origin(origin='*')
def uploadToS3Bucket(user_id):
	bucket_name = "myelsapython"
	s3 = boto3.client(
		"s3",
		aws_access_key_id=ACCESS_KEY,
		aws_secret_access_key=SECRET_KEY
		)
	bucket_resource = s3
	uploadedfile = request.files['file']
	print(uploadedfile)
	filename = ''
	userKey = 'myelsa_academy/'+user_id+'/'
	fpath = ''
	FileSize = None
	if uploadedfile:
		filename = secure_filename(uploadedfile.filename)
		keyname = userKey+filename
		uploadRes = bucket_resource.upload_fileobj(
			Bucket = bucket_name,
			Fileobj=uploadedfile,
			Key=keyname)
		print(uploadRes)
		return jsonify({"attributes": {"status": "success"},
			"responseList": [{
			  "FilePath": "https://d1lwvo1ffrod0a.cloudfront.net/{}".format(keyname),
			  "FileName": filename,
			  "FileSize": FileSize}],
			"responseDataTO": {}
			})
	else:
		return jsonify({"attributes": {"status": "success"},
					"responseList": [],
					"responseDataTO": {}
				})



@academy_course_details.route("/getUserSubmissionsByAssessmentId/<int:user_id>/<int:module_id>/<int:assessment_id>")
@cross_origin(origin='*')
def getUserSubmissionsByAssessmentId(user_id,module_id,assessment_id):

	connection = creamson_academy_connection()
	cursor = connection.cursor()

	cursor.execute("""SELECT `user_assessment_filepath`,`filetype`,`last_update_ts` as 'submisssion_date' FROM `user_assessment_mapping` 
		WHERE `user_id`= %s and `module_id` = %s and `assessment_id` = %s""",(user_id,module_id,assessment_id))

	fileDtls = cursor.fetchall()
	for fid, file in enumerate(fileDtls):
		file['submisssion_date'] = file.get('submisssion_date').isoformat()


	return jsonify({"attributes": {"status_desc": "User assessment files",
							"status": "success"},
			"responseList":fileDtls})



@academy_course_details.route("/postUserAssessmentFiles",methods=['POST'])
@cross_origin(origin='*')
def postUserAssessmentFiles():

	connection = creamson_academy_connection()
	cursor = connection.cursor()

	details = request.get_json()
	user_id = details.get('user_id')
	module_id = details.get('module_id')
	assessment_id = details.get('assessment_id')
	filename = details.get('filename')
	filetype = details.get('filetype')

	fileInsertQuery = ("""INSERT INTO `user_assessment_mapping`(`user_id`, `module_id`, 
		`assessment_id`, `user_assessment_filepath`, `filetype`) VALUES (%s,%s,%s,%s,%s)""")

	fileData = (user_id,module_id,assessment_id,filename,filetype)

	cursor.execute(fileInsertQuery,fileData)

	connection.commit()
	cursor.close()

	getUserAssessmentURL = BASE_URL + 'academy_course_section/getUserSubmissionsByAssessmentId/{}/{}/{}'.format(user_id,module_id,assessment_id)

	assessmentDtls = requests.get(getUserAssessmentURL,verify=False).json().get('responseList')

	return jsonify({"attributes": {"status_desc": "User assessment files",
									"status": "success"},
					"responseList":assessmentDtls})


@academy_course_details.route("/getQuestionsByAssessmentId/<int:assessment_id>")
@cross_origin(origin='*')
def getQuestionsByAssessmentId(assessment_id):
	connection = creamson_academy_connection()
	cursor = connection.cursor()

	cursor.execute("""SELECT `Question_ID`  FROM `assessment_question_mapping` 
		WHERE `Assessment_ID` = %s""",(assessment_id))

	questionIdList = cursor.fetchall()
	questionList = []
	if questionIdList:
		for qid in questionIdList:

			cursor.execute("""SELECT ques.`Question_Type`,ast.`Assessment_Type_Desc`,ques.`Question_ID`,
				ques.`Question`,ques.`Content_file_path`,ques.`Content_FileName`,ques.`File_Type_ID`,
				ques.`negative_marks`,ques.`level`,ques.`marks`,GROUP_CONCAT((SELECT op1.`option` 
				FROM OPTIONS op1 WHERE op1.`option_ID` = ans.`Option_ID`) SEPARATOR '|') answer,
				GROUP_CONCAT(ans.`Option_ID` SEPARATOR '|') AS 'correct_optionId',
				GROUP_CONCAT(ans.`Additional_Text` SEPARATOR '|') AS 'Additional_Text',
				GROUP_CONCAT((SELECT op1.`Content_file_path` FROM OPTIONS op1 WHERE 
				op1.`option_ID` = ans.`Option_ID`) SEPARATOR '|') AS 'answer_filepath'
				FROM `question` ques,`answer` ans,`options` op,`assessment_type` ast WHERE
				ques.`Question_ID` = ans.`Question_ID` AND ans.`Option_ID` = op.`Option_ID` 
				AND  ast.`Assessment_Type_ID` = ques.`Question_Type` 
				AND ques.`Question_ID` = %s""",(qid.get('Question_ID')))


			questionDtls = cursor.fetchone()
			answers = []
			if questionDtls:
				answers.append({'answer':questionDtls.get('answer'),
					'correct_optionId':questionDtls.get('correct_optionId'),
					'answer_filepath':questionDtls.get('answer_filepath'),
					'Additional_Text':questionDtls.get('Additional_Text')})

				questionDtls.pop('answer')
				questionDtls.pop('correct_optionId')
				questionDtls.pop('answer_filepath')
				questionDtls.pop('Additional_Text')
				cursor.execute("""SELECT `Option_ID`, `Question_ID`, `Option`, `Option_Sequence_ID`,
					`Content_file_path`, `Content_FileName`, `File_Type_ID` 
					FROM `options` WHERE `Question_ID` = %s""",(qid.get('Question_ID')))

				options = cursor.fetchall()
				questionDtls['options'] = options
				questionDtls['answers'] = answers

				questionList.append(questionDtls)

	cursor.close()
	return ({"attributes": {"status_desc": "Question Details",
							"status": "success"
								},
			"responseList":questionList}), status.HTTP_200_OK




@academy_course_details.route("/submitQuizAnswers", methods=['POST'])
@cross_origin(origin='*')
def submitQuizAnswers():
	details = request.get_json()
	connection = creamson_academy_connection()
	cursor = connection.cursor()
	# currentDate = date.today().strftime("%d%b%y")

	queoptans = details['quizDtls']
	assessment_id = queoptans[0].get('assessment_id')
	user_id = queoptans[0].get('user_id')
	for que in queoptans:
		assessment_id = que.get('assessment_id')
		user_id = que.get('user_id')
		question_id = que.get('question_id')
		option_id = que.get('option_id')
		answer = que.get('answer')
		marks = que.get('marks')

		cursor.execute("""SELECT ques.`Question_Type`, ast.`Assessment_Type_Desc`, ques.`Question_ID`,
			ques.`Question`, ques.`Content_file_path`, 
			ques.`Content_FileName`, ques.`File_Type_ID`, ques.`negative_marks`,ques.`marks`,
			GROUP_CONCAT((select op1.`option` from options op1 where op1.`option_ID` = ans.`Option_ID`) SEPARATOR '|') answer, 
			GROUP_CONCAT(ans.`Option_ID` SEPARATOR '|') as 'correct_optionId', GROUP_CONCAT(ans.`Additional_Text` SEPARATOR '|') as 'Additional_Text'
			FROM `question` ques, `answer` ans, `options` op, 
			`assessment_type` ast WHERE ques.`Question_ID` = ans.`Question_ID` 
			AND ans.`Option_ID` = op.`Option_ID`  AND ast.`Assessment_Type_ID` = ques.`Question_Type` 
			AND ques.`Question_ID` = %s""",(question_id))

		correctAnsDtls = cursor.fetchone()
		question_type = correctAnsDtls.get('Assessment_Type_Desc')

		if question_type == 'MSQ':
			studentAns = option_ID.split(',')
			correctAns = correctAnsDtls.get('correct_optionId').split('|')
			if collections.Counter(studentAns) == collections.Counter(correctAns):
				# print(correctAns,studentAns)
				marks = correctAnsDtls.get('marks')
				answer_flag = 'correct'
			else:
				marks = correctAnsDtls.get('negative_marks')
				answer_flag = 'incorrect'
		elif question_type == 'MCQ':
			if option_id == correctAnsDtls.get('correct_optionId'):
				marks = correctAnsDtls.get('marks')
				answer_flag = 'correct'
			else:
				marks = correctAnsDtls.get('negative_marks')
				answer_flag = 'incorrect'
		student_ans_query = ("""INSERT INTO `student_answers`(`Assessment_ID`, 
			`user_id`, `Question_ID`, `Option_ID`, `Answer`, `marks`,`answer_flag`) 
			VALUES (%s,%s,%s,%s,%s,%s,%s)""")
		student_ans_data = (assessment_id,user_id,question_id,option_id,answer,marks,answer_flag)
		cursor.execute(student_ans_query,student_ans_data)
		connection.commit()
	try:
		statusInsertQuery = ("""INSERT INTO `user_assessment_status_mapping`(`user_id`, `assessment_id`, 
			`status`, `marks`) VALUES (%s,%s,%s,%s)""")

		cursor.execute(statusInsertQuery,(user_id,assessment_id,'complete',0))
		connection.commit()
	except:
		pass
	cursor.close()
	return jsonify({"attributes": {"status_desc": "Question Details",
									"status": "success"},
					"responseList":'success'})


@academy_course_details.route("/getAdditionalResourcesByModuleId/<int:user_id>/<int:module_id>/<int:course_id>")
@cross_origin(origin='*')
def getAdditionalResourcesByModuleId():
	connection = creamson_academy_connection()
	cursor = connection.cursor()
	cursor.execute("""SELECT ucm.`course_id`,`course_name` FROM `user_course_mapping` ucm, 
		`course` co WHERE `user_id` = %s and ucm.`course_id` = %s""",(user_id,course_id))

	subCourse = cursor.fetchone()
	msg = 'not-found'
	course_name = None
	addResourceDtls = []
	if subCourse:

		cursor.execute("""SELECT mam.`add_resource_id`,`resource_name`,`resource_type`,
			`resource_url` FROM `module_additional_resource_mapping` mam INNER JOIN 
			`additional_resources` ar on mam.`add_resource_id` = ar.`add_resource_id` 
			WHERE `course_id` = %s and `module_id` = %s""",(course_id,module_id))

		addResourceDtls = cursor.fetchall()
		msg = 'found'
		course_name = subCourse.get('course_name')

	return ({"attributes": {"status_desc": "Additional Resources List",
							"status": "success",
							"course_name":course_name,
							"msg":msg},
			"responseList":addResourceDtls})