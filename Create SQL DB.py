import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd = '' #insert your password
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE boombastic")