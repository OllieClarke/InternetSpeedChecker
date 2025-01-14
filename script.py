from dotenv import load_dotenv
import os
import speedtest
import snowflake.connector
import datetime

#Use speedtest-cli to find information
try:
    #Using Speedtest to find my upload, download and ping
    #setup speedtest using https
    st = speedtest.Speedtest(secure=True)

    #find the best server
    st.get_best_server()

    #Get download/upload/ping/timestamp
    download_speed = st.download()
    upload_speed = st.upload()
    ping = st.results.ping
    timestamp = datetime.datetime.now()

    # build json string
    output = '{"Download": '+str(download_speed)+', "Upload": '+str(upload_speed)+', "Ping": '+str(ping)+', "Timestamp": '+str(timestamp)+'}'

except:
    #If it fails then make a null json, but with a timestamp
    timestamp = datetime.datetime.now()
    output= '{"Download": null, "Upload": null, "Ping": null, "Timestamp": '+str(timestamp)+'}'

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

    #execute the sql binding data for safety
    cur.execute("INSERT INTO %(table)s(JSON, __UPLOADED) "
                "VALUES ('%(output)s', '%(uploaded)s')"
                ,{'table':table,
                  'output':output,
                  'uploaded':uploaded})
finally:
    #end the connection
    cur.close()