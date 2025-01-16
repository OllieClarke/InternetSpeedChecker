from dotenv import load_dotenv
import os
import snowflake.connector
import datetime
import json

# Open the file in read mode and read the entire content as a string
with open('speedoutput.txt', 'r') as file:
    content = file.read()

# edit the json to remove server and client 
# Convert string to dictionary
data = json.loads(content) 

print(data)
# Remove 'interface' info
data.pop('interface', None)

# Rename keys to title case
data = {key.title(): value for key, value in data.items()}

# Convert back to string
output = json.dumps(data, indent=4)


#Pull in values from secrets
load_dotenv()
username = os.getenv("USER_NAME")
password = os.getenv("PASSWORD")
account = os.getenv("ACCOUNT")
role = os.getenv("ROLE")
warehouse = os.getenv("WAREHOUSE")
database = os.getenv("DATABASE")
schema = os.getenv("SCHEMA")
table = os.getenv("TABLE")

#make a connection to snowflake
conn = snowflake.connector.connect(
    user=username,
    password=password,
    account=account,
    warehouse=warehouse,
    database=database,
    schema=schema
    )

#create a cursor
cur = conn.cursor()

#try and load the values into the table
try:
    #get now
    uploaded = datetime.datetime.now()

    #make sql with parameter binding
    sql = "INSERT INTO INTERNET_SPEED_TEST(JSON, __UPLOADED) "
    sql += "VALUES (%s, %s)"
    
    #execute the sql binding data for safety
    cur.execute(sql,(output, uploaded))
finally:
    #end the connection
    cur.close()