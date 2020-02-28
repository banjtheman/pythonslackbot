#!/bin.bash
#start nginx
sudo service nginx start
#start backend app
gunicorn --bind 0.0.0.0:5035 --timeout 600 --workers=1 --reload app &
#stay up forever
tail -f /dev/null
