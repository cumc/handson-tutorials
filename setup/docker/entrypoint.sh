#!/bin/bash
set -e
cd $HOME
curl -fsSL https://raw.githubusercontent.com/cumc/handson-tutorials/main/setup/course_entrypoint.sh | bash
cd $HOME/handson-tutorials/contents
jupyter-lab
