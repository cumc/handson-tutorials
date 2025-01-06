#!/bin/bash
set -e
mkdir -p /home/ubuntu/bin
export PATH="/home/ubuntu/bin:${PATH}"
cd $HOME
curl -fsSL https://raw.githubusercontent.com/cumc/handson-tutorials/main/setup/course_entrypoint.sh | bash
cd $HOME/handson-tutorials/contents
jupyter-lab
