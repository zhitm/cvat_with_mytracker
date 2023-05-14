#!/usr/bin/env bash



python3 save_ip_in_file.py

#run serverless function
nuctl deploy --project-name cvat   --path serverless/pytorch/dschoerk/transt/nuclio   --volume `pwd`/serverless/common:/opt/nuclio/common



#run my tracker
cd mytrackerDocker
docker build -t myserver .
docker run --rm -i --name mytracking -p 8083:8083 myserver &
