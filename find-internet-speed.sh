#!/bin/bash
#make a timestamp command
timestamp() {
  date +%F_%T
}

timestamp #print timestamp
#say where we're going
echo changing directory to InternetSpeedChecker
cd /home/pi/InternetSpeedChecker/

timestamp #print timestamp
#install requirements
# superceded by using a virtual environment and installing requirements there.
# echo installing requirements
# /home/pi/.local/bin/pip3.12 install -r requirements.txt

timestamp #print timestamp
echo delete old result if exists
if [ ! -f speedoutput.txt ]; then
    echo "no previous output"
else 
  rm speedoutput.txt
fi

timestamp #print timestamp
#run the speedtest and output to an output.txt file
echo run cli
if ! /usr/bin/speedtest --accept-license --accept-gdpr --format=json > speedoutput.txt; then
  echo "speedtest failed, aborting"
  exit 1
fi

timestamp #print timestamp
#run python script
echo running python script
/home/pi/InternetSpeedChecker/.venv/bin/python script.py

#Add final timestamp
timestamp #print timestamp
echo finished
