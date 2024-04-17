FROM ghcr.io/prefix-dev/pixi:latest
USER root
# For security reasons, SSL certificates and timezone database must be installed by host package manager
RUN apt-get update && apt-get -y install ca-certificates tzdata libgl1 libgomp1
# Use bash as default shell instead of dash
RUN ln -sf /bin/bash /bin/sh  

RUN useradd --no-log-init --create-home --shell /bin/bash --uid 1000 --no-user-group jovyan
USER jovyan

# Copy over configs and environments
COPY --chown=jovyan r_libs.yml /tmp
COPY --chown=jovyan python_libs.yml /tmp
COPY --chown=jovyan global_packages /tmp
COPY --chown=jovyan init.sh /tmp
COPY --chown=jovyan fixes.sh /tmp

RUN mkdir -p /home/jovyan/.config/pixi && \
    echo 'default_channels = ["dnachun", "conda-forge", "bioconda"]' > /home/jovyan/.config/pixi/config.toml

# Install global packages with pixi
RUN pixi global install $(tr '\n' ' ' < /tmp/global_packages)
ENV PATH="/home/jovyan/.pixi/bin:${PATH}"

# Install R and Python libraries with micromamba (will replace with pixi in future)
RUN micromamba config prepend channels nodefaults 
RUN micromamba config prepend channels bioconda
RUN micromamba config prepend channels conda-forge
RUN micromamba config prepend channels dnachun
RUN micromamba shell init --shell=bash /home/jovyan/micromamba
RUN micromamba env create --yes --quiet --file /tmp/r_libs.yml;
RUN micromamba env create --yes --quiet --file /tmp/python_libs.yml;
RUN micromamba clean --all --yes

# Set path for R and Python libraries
RUN bash /tmp/init.sh

# Run some customized fixes
RUN bash /tmp/fixes.sh

# Clean up
RUN rm -rf /tmp/*

COPY  --chown=jovyan --chmod=755 entrypoint.sh /home/jovyan/entrypoint.sh
COPY  --chown=jovyan --chmod=644 .synapseConfig /home/jovyan/entrypoint.sh
ENV PYDEVD_DISABLE_FILE_VALIDATION=1
WORKDIR /home/jovyan
CMD ["/bin/bash", "/home/jovyan/entrypoint.sh"]
