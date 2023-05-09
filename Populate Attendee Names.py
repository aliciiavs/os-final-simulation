from faker import Faker
import mysql.connector

cnx = mysql.connector.connect(user="root",
                              password="",  #insert your password
                              host="127.0.0.1",
                              database="boombastic")


fake = Faker('es_ES')
cursor = cnx.cursor()
# Generate 100 Spanish names with Faker

for i in range(100):
    first_name = fake.first_name()
    last_name = fake.last_name()
    full_name = f"{first_name} {last_name}"
    query = f"INSERT INTO attendee_names (id, name) VALUES ({i}, '{full_name}')"
    cursor.execute(query)
    cnx.commit()

# Close the cursor and connection
cursor.close()
cnx.close()