from dotenv import load_dotenv
import os
import speedtest
import time

#Get starttime
start_time = time.time()

#Pull in username and password from secrets
load_dotenv()
username = os.getenv("USER_NAME")
password = os.getenv("PASSWORD")

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
    timestamp = time.time()

    # build json string
    output = '{"Download": '+str(download_speed)+', "Upload": '+str(upload_speed)+', "Ping": '+str(ping)+', "Timestamp": '+str(timestamp)+'}'

except:
    #If it fails then make a null json, but with a timestamp
    timestamp = time.time()

    output= '{"Download": null, "Upload": null, "Ping": null, "Timestamp": '+str(timestamp)+'}'

print(output)
