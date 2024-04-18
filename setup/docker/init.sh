#!/usr/bin/env bash
set -o errexit -o xtrace
# Only show PYTHONPATH and R_LIBS to specific executables
export HOME="/home/jovyan"
sed -i '2i export PYTHONPATH="${HOME}/micromamba/envs/python_libs/lib/python3.12/site-packages"' ${HOME}/.pixi/bin/python
sed -i '2i export PYTHONPATH="${HOME}/micromamba/envs/python_libs/lib/python3.12/site-packages"' ${HOME}/.pixi/bin/python3
sed -i '2i export PYTHONPATH="${HOME}/micromamba/envs/python_libs/lib/python3.12/site-packages"' ${HOME}/.pixi/bin/jupyter-lab
sed -i '2i export PYTHONPATH="${HOME}/micromamba/envs/python_libs/lib/python3.12/site-packages"' ${HOME}/.pixi/bin/jupyter-server
sed -i '2i export PYTHONPATH="${HOME}/micromamba/envs/python_libs/lib/python3.12/site-packages"' ${HOME}/.pixi/bin/sos
echo "unset PYTHONPATH" >> ${HOME}/.bashrc
echo ".libPaths('${HOME}/micromamba/envs/r_libs/lib/R/library')" >> ${HOME}/.Rprofile

# pixi global currently gives it wrappers all lowercase names, so we need to make symlinks for R and Rscript
if [ ! -e "${HOME}/.pixi/bin/R" ]; then
  ln -sf "${HOME}/.pixi/bin/r" "${HOME}/.pixi/bin/R"
fi

if [ ! -e "${HOME}/.pixi/bin/Rscript" ]; then
  ln -sf "${HOME}/.pixi/bin/rscript" "${HOME}/.pixi/bin/Rscript"
fi

# Register Juypter kernels
find ${HOME}/micromamba/envs/python_libs/share/jupyter/kernels/ -maxdepth 1 -mindepth 1 -type d | \
    xargs -I % jupyter-kernelspec install --user %
find ${HOME}/micromamba/envs/r_libs/share/jupyter/kernels/ -maxdepth 1 -mindepth 1 -type d | \
    xargs -I % jupyter-kernelspec install --user %

# Jupyter configurations
mkdir -p $HOME/.jupyter
curl -o $HOME/.jupyter/jupyter_lab_config.py https://raw.githubusercontent.com/gaow/misc/master/bash/pixi/jupyter_lab_config.py
curl -o $HOME/.jupyter/jupyter_server_config.py https://raw.githubusercontent.com/gaow/misc/master/bash/pixi/jupyter_server_config.py
