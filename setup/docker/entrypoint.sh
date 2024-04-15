#!/bin/bash
set -e
curl -o /tmp/course_entrypoint.sh https://raw.githubusercontent.com/cumc/handson-tutorials/main/setup/course_entrypoint.sh
chmod +x /tmp/course_entrypoint.sh
bash /tmp/course_entrypoint.sh

cd /root/handson-tutorials/
jupyter-lab
