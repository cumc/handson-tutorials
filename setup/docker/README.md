# Basic environments


> **Note:** This example get started guide is in MacOS environment.

*Host Environment*
```
yiweizh@Yiweis-MacBook-Pro:~$ sw_vers
ProductName:		macOS
ProductVersion:		14.4
BuildVersion:		23E214
```

*Docker Version*
```
yiweizh@Yiweis-MacBook-Pro:~$ docker --version
Docker version 24.0.7, build afdd53b
```

# Build the handout container images

### Get the handson-tutorials repository
Clone the handson-tutorials repository on your local computer.
```
git clone git@github.com:cumc/handson-tutorials.git
```

### Go to the source code directory
The dockerfile and other materials for building the container are located under `setup/docker/`. Note that the path of the repository stored on your local machine would be different from the example.

```bash
# Go to the source code directorys
handson-tutorials $ cd setup/docker

# Directory structure
docker $ tree
.
├── Dockerfile
├── entrypoint.sh
├── fixes.sh
├── global_packages
├── init.sh
├── python_libs.yml
└── r_libs.yml

1 directory, 7 files
```

### Build the container
Using `docker build` command to build the container. Make sure to specify the `--platform` option so that it is built in linux AMD64 architecture. You could tag the container name as you preferred.

```bash
docker build --platform linux/amd64 -t gaow/handson-tutorials:latest -f Dockerfile .
```
Example output:
```
docker build --platform linux/amd64 -t gaow/handson-tutorials:latest -f Dockerfile .

[+] Building 1.1s (28/28) FINISHED                                                                   docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                 0.0s
 => => transferring dockerfile: 1.51kB                                                                               0.0s
 => [internal] load .dockerignore                                                                                    0.0s
 => => transferring context: 2B                                                                                      0.0s
 => [internal] load metadata for ghcr.io/prefix-dev/pixi:latest                                                      1.0s
 => [internal] load build context                                                                                    0.0s
 => => transferring context: 190B                                                                                    0.0s
 => [ 1/23] FROM ghcr.io/prefix-dev/pixi:latest@sha256:61c73abba6119648b9de1adc6a2547e2bf0e556b1d06a8dd65d3152afb49  0.0s
 => CACHED [ 2/23] RUN apt-get update && apt-get -y install ca-certificates tzdata curl unzip                        0.0s
 => CACHED [ 3/23] COPY r_libs.yml /tmp                                                                              0.0s
 => CACHED [ 4/23] COPY python_libs.yml /tmp                                                                         0.0s
 => CACHED [ 5/23] COPY global_packages /tmp                                                                         0.0s
 => CACHED [ 6/23] COPY init.sh /tmp                                                                                 0.0s
 => CACHED [ 7/23] COPY fixes.sh /tmp                                                                                0.0s
 => CACHED [ 8/23] RUN mkdir -p /root/.config/pixi &&     echo 'default_channels = ["dnachun", "conda-forge", "bioc  0.0s
 => CACHED [ 9/23] RUN ln -sf /bin/bash /bin/sh                                                                      0.0s
 => CACHED [10/23] RUN pixi global install $(tr '\n' ' ' < /tmp/global_packages)                                     0.0s
 => CACHED [11/23] RUN micromamba config prepend channels nodefaults                                                 0.0s
 => CACHED [12/23] RUN micromamba config prepend channels bioconda                                                   0.0s
 => CACHED [13/23] RUN micromamba config prepend channels conda-forge                                                0.0s
 => CACHED [14/23] RUN micromamba config prepend channels dnachun                                                    0.0s
 => CACHED [15/23] RUN micromamba shell init --shell=bash /root/micromamba                                           0.0s
 => CACHED [16/23] RUN micromamba env create --yes --quiet --file /tmp/r_libs.yml;                                   0.0s
 => CACHED [17/23] RUN micromamba env create --yes --quiet --file /tmp/python_libs.yml;                              0.0s
 => CACHED [18/23] RUN micromamba clean --all --yes                                                                  0.0s
 => CACHED [19/23] RUN bash /tmp/init.sh                                                                             0.0s
 => CACHED [20/23] RUN bash /tmp/fixes.sh                                                                            0.0s
 => CACHED [21/23] RUN rm -rf /tmp/*                                                                                 0.0s
 => CACHED [22/23] COPY entrypoint.sh /root/entrypoint.sh                                                            0.0s
 => CACHED [23/23] RUN chmod +x /root/entrypoint.sh                                                                  0.0s
 => exporting to image                                                                                               0.0s
 => => exporting layers                                                                                              0.0s
 => => writing image sha256:891cdcf643c9ec45dac9505519841e15f319a309db489341d1622cc309c41f8f                         0.0s
 => => naming to docker.io/gaow/handson-tutorials:latest                                                        0.0s

View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/tvgi1279d3fgb9cl6xahdz1bv

What's Next?
  View a summary of image vulnerabilities and recommendations → docker scout quickview
```

Check the image has been built successfully.
```bash
docker $ docker images
REPOSITORY                    TAG        IMAGE ID       CREATED        SIZE
gaow/handson-tutorials   latest     891cdcf643c9   6 hours ago    14GB
```

### Verify the docker images locally
You could use `docker run` to validate the image locally.
```
docker run --platform linux/amd64 -d -p 8888:8888 <Image ID>
```
 Note that the AWS s3 sync data part will retrieve credentials from the environment variables, which would be automatically set if only launched on MemVerge Memory Machine Cloud (MMC). If run locally, the AWS s3 CLIs would fail to sync data as there are no credentials being set.

### Push to the dockerhub (optional)
For enabling the container image to be pulled by the MMC later, you could push the container image to a public dockerhub.
```
docker push gaow/handson-tutorials:latest
```
