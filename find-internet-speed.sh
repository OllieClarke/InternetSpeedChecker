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
echo installing requirements
python3.12 -m pip install -r requirements.txt

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
/usr/bin/speedtest --json > speedoutput.txt

timestamp #print timestamp
#run python script
echo running python script
/usr/local/bin/python3.12 script.py

#Add final timestamp
timestamp #print timestamp
echo finished
