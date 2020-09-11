import pymysql

def creamson_academy_connection():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_academy',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection