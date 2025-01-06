FROM ubuntu:latest
USER root
# For security reasons, SSL certificates and timezone database must be installed by host package manager
# libgl1 is needed for the conda-forge mesa CDT for OpenGL support
# libgomp1 is needed for FINEMAP, which is precompiled and breaks with RPATH relocation
# tmate is needed so that SSH access is possible
# curl is needed to bootstrap pixi
RUN apt-get update && apt-get -y install ca-certificates tzdata libgl1 libgomp1 tmate curl

# Use bash as default shell instead of dash
RUN ln -sf /bin/bash /bin/sh

USER ubuntu
ENV PYDEVD_DISABLE_FILE_VALIDATION=1
ENV LC_ALL="C"
ENV USER=ubuntu
ENV OPENBLAS_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV NUMEXPR_MAX_THREADS=1
WORKDIR /home/ubuntu
