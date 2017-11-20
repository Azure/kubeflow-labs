# Docker

### Prerequisites  
* [Understand the learning objectives](../learningObjectives.md)

### Summary

In this section you will learn about :
* Running Docker locally
* Basics of Docker
* Containerizing a simple application
* Building and Pushing a Image

### Excercice

#### Setup Docker locally

The official documentation from *docs.docker.com* is very well detailed for setting up Docker locally depending your OS :
* [Mac](https://docs.docker.com/docker-for-mac/)
* [Linux](https://docs.docker.com/engine/installation/linux/) 
* [Windows](https://docs.docker.com/docker-for-windows/)

Once you are done installing Docker, test your Docker installation by running the following from the docker-cli (Terminal or Powershell):
```bash
$ docker run -it --rm hello-world
```

You should see the following results : 
```bash
$ docker run -it --rm hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
5b0f327be733: Pull complete
Digest: sha256:07d5f7800dfe37b8c2196c7b1c524c33808ce2e0f74e7aa00e603295ca9a0972
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://cloud.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/engine/userguide/
...
```

#### Basics of Docker

#### Containerizing a simple application
#### Building and Pushing a Image



### Useful Links
* [What is Docker ?](https://www.docker.com/what-docker)
* [Docker for Mac](https://store.docker.com/editions/community/docker-ce-desktop-mac)
* [Docker for Windows](https://store.docker.com/editions/community/docker-ce-desktop-windows)
* [Docker for Ubuntu](https://store.docker.com/editions/community/docker-ce-server-ubuntu)
* [Docker for beginner](https://github.com/docker/labs/blob/master/beginner/readme.md)

### Expected Result

Doing a `kubectl describe pod <pod-name>` should show...