#!/bin/bash
set -e
curl -fsSL https://raw.githubusercontent.com/cumc/handson-tutorials/main/setup/course_entrypoint.sh | bash
cd /home/jovyan/handson-tutorials/contents
jupyter-lab
