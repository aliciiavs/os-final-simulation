# Script to populate the snapshots table in sql after the simulation has run.
# This helps us have a summary of how many people in each place at a time.

import mysql.connector

cnx = mysql.connector.connect(user="root",
                              password="",  #insert your password
                              host="127.0.0.1",
                              database="boombastic")

cursor = cnx.cursor()

for time in range(0, 881):
    # Execute the query for the current snapshot time
    query = f"""SELECT 
                  l.location,
                  COUNT(a.location) AS count
                FROM
                  (SELECT DISTINCT location FROM boombastic.attendees) l 
                  LEFT OUTER JOIN boombastic.attendees a
                    ON a.location = l.location
                    AND a.arrived <= {time}
                    AND a.moved > {time}
                GROUP BY l.location
    """
    cursor.execute(query)
    # Fetch the results and insert them into the snapshots table
    results = cursor.fetchall()
    for row in results:
        insert_query = f"INSERT INTO snapshots (time, location, count,datetime) VALUES ({time}, '{row[0]}', {row[1]},FROM_UNIXTIME((({time} * 60*6) + UNIX_TIMESTAMP('2023-07-21 00:00:00'))))"
        cursor.execute(insert_query)
        cnx.commit()

# Close the cursor and connection
cursor.close()
cnx.close()