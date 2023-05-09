import mysql.connector


mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd = '' , #insert your password
    database = 'boombastic'
)




mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE attendees (id int, arrived decimal(5,2), moved decimal(5,2), location VARCHAR(255))")


mycursor.execute("CREATE TABLE stages (location VARCHAR(255),artist VARCHAR(255), start decimal(5,2), finish decimal(5,2))")


mycursor.execute("create table attendee_names (id int,name VARCHAR(255))")

# Create a new table for the results
query = """
CREATE TABLE snapshots (
  time INT,
  location VARCHAR(255),
  count INT,
  datetime datetime
)
"""

mycursor.execute(query)