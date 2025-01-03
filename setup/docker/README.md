## Basic environments


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

## Build the handout container images

This is more or less a ["bare metal" image](https://github.com/danielnachun/misc-containers/tree/main/tmate-minimal) with a [customized start-up script](https://github.com/cumc/handson-tutorials/blob/main/setup/course_entrypoint.sh) to configure additional environments, in particular downloading data for local uses. This image must be launched in a specific way to mount pre-installed software packages. The complete setup guide for software pre-installation on MMCloud can be [found on this page](https://wanggroup.org/productivity_tips/mmcloud-interactive).

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
├── README.md
├── entrypoint.sh
├── global_packages.txt
├── python_packages.txt
└── r_packages.txt

1 directory, 6 files
```

### Build the container
Using `docker build` command to build the container. Make sure to specify the `--platform` option so that it is built in linux AMD64 architecture. You could tag the container name as you preferred.

```bash
docker build --platform linux/amd64 -t gaow/handson-tutorials:latest -f Dockerfile .
```

Check the image has been built successfully.
```bash
docker $ docker images
REPOSITORY                    TAG        IMAGE ID       CREATED        SIZE
gaow/handson-tutorials   latest     891cdcf643c9   6 hours ago    3GB
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
