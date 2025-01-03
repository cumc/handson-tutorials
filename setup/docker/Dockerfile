FROM quay.io/danielnachun/tmate-minimal:latest
RUN mkdir -p /home/ubuntu/bin
COPY  --chown=ubuntu --chmod=755 entrypoint.sh /home/ubuntu/bin/entrypoint.sh
WORKDIR /home/ubuntu
CMD ["/bin/bash", "/home/ubuntu/bin/entrypoint.sh"]
