from flask import Flask
from flask import render_template
from flask import request
import pandas
import csv
from flask_mysqldb import MySQL
import MySQLdb.cursors as cursors
import MySQLdb
import mysql.connector
from os import path,walk


app = Flask(__name__)

mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	password="",
	database="forclosure"
)

cursor = mydb.cursor(buffered=True, dictionary = True)

@app.route('/', methods=['GET', 'POST'])


def root():

	# Get data from DB
	sql = "SELECT * FROM content WHERE county=%s ORDER BY last_edited DESC"
	val = ('ATLANTIC',)
	cursor.execute(sql, val)
	datas = cursor.fetchall()

	# fields name that you want to show
	colnames =['name','address','city','county','sales_date','status','last_edited','link']

	# get input from the website, update the data in db, and get back to root
	if request.method == 'POST' and len(request.form.get('user_csv')) >= 30 :
		results = []

		# user input from FORM
		user_input = 'name,address,city,sales_date,upset_amount,county,attorney,status,status_date,link\n' + request.form.get('user_csv')
		print(user_input)
		user_csv = user_input.split('\n')
		reader = csv.DictReader(user_csv)

		for row in reader:
			#update to db
			update_db(dict(row))

		#change method to Get
		request.method = 'GET'
		return root()
	
	return render_template('home.html', results = datas, colnames = colnames)
	
def update_db(doc):

	sql = "SELECT * FROM content WHERE name=%s AND address=%s AND city=%s AND county=%s"
	val = (doc['name'], doc['address'], doc['city'], doc['county'])
	cursor.execute(sql, val)
	datas = cursor.fetchall()

	if len(datas) > 0:
		sql = "UPDATE content SET status=%s WHERE name=%s AND address=%s AND city=%s AND county=%s"
		val = (doc['status'], doc['name'], doc['address'], doc['city'], doc['county'])
		cursor.execute(sql, val)
		mydb.commit()
		print('DATA_EDITED')
	else:
		print('DB_WARNING, NO DATA, INSERTED NEW ONE')
		sql = "INSERT INTO content (name,address,city,county,sales_date,status,status_date,link,last_crawled) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		val = (doc['name'],doc['address'], doc['city'], doc['county'], doc['sales_date'], doc['status'], doc['status_date'], doc['link'], doc['last_crawled'])
		cursor.execute(sql, val)
		mydb.commit()


if __name__ == '__main__':
	extra_dirs = ['templates',]
	extra_files = extra_dirs[:]
	for extra_dir in extra_dirs:
	    for dirname, dirs, files in walk(extra_dir):
	        for filename in files:
	            filename = path.join(dirname, filename)
	            print(filename)
	            if path.isfile(filename):
	                extra_files.append(filename)
	app.run(debug=True,extra_files=extra_files)