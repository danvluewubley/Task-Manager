import mysql.connector
import os
import dotenv

dotenv()

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd=os.getenv("SQL_PASSWORD")
)

my_cursor=mydb.cursor()

# my_cursor.execute("CREATE DATABASE tasks")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
  print(db)