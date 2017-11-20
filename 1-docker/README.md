# Docker

### Prerequisites  
* [Understand the learning objectives](../learningObjectives.md)

### Summary

In this section you will learn about :
* Running Docker locally
* Basics of Docker
* Containerizing a simple application
* Building and Pushing a Image

### Setup Docker locally

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

This command will run a container locally from the image named : `hello-world`

### Basics of Docker

You can see all the commands running `docker --help` from your terminal or powershell.

#### Base image and registry

All containers contains **layers**. Those layers are customizations such as tools installations, scripts and more. 

In a really high level example, if you want an ubuntu image with python3 installed and the Azure CLI, you have to think about the following steps :
- Install ubuntu
- Install python3 from apt-get
- Install Azure CLI from a script

With Docker, those 3 steps are considered as layers. Those layers can already be prebuilt, to avoid all the installation time, and called **base image**.

Those **base images** can be built and used locally, or pulled from a **registry**. This **registry** could be either public or private. One of the most popular one and official at Docker is called : [Docker Hub](https://hub.docker.com/)

If you look at the [Docker Hub](https://hub.docker.com/) and do some search you can find a multiple of **official images** such as : Ubuntu, Redis, Nginx, Mongo and more...

> You can also search from your terminal using the `docker search` command line.

We will explain later how build locally you own image.

#### Command line

We will describe the most important command to start with in this section.

1. `docker run OPTIONS IMAGE COMMAND`
    
    The docker `run` command allow to start a container, with different options, from a base image.

    Popular OPTIONS :

    |Option|Description|Scenario|
    |-|-|-|
    |-it|Interactive mode (-i and -t combined)|When you need a prompt in the container
    |-d|Detached|When you want to run you container in the background such as scripts or server.
    |-P|Map the necessary port in the container to the host using random one|When you want to reach a port in your container, for example the port 80 for a web server
    |-P|Map some specific port in the container to specific host one |When you want to reach a port in your container, for example the port 80 for a web server
    |-e|Inject a environment variable|When you are using environement variables in your script such as connection string
    |-v|Mount a folder from the host in the container|When you want to modify files in your container such as configuration or codes for example, without to restart a new one
    |--name|Give a name to the container|When you want to identify your containers
    |--rm|Automatically delete the process at then end of the execution|When you are creating / removing all the time your containers

    > Those options can be combined

    IMAGE : Base image that you want to use. An image also have a concept of `tags`, we will explain it later.

    COMMAND (Optional) : Command to run inside your container

    Examples
    
    |Command|Description|
    |-|-|
    |`docker run -it --rm --name myUbuntuContainer ubuntu /bin/bash`|Run an official Ubuntu image in an interactive mode with the bash|
    |`docker run -d --rm --name SimpleWebServer nginx`|Run an official Nginx image in a detached mode named SimpleWebServer|
    |`docker run -d --rm -P nginx`|Run an official Nginx image in a detached mode and mapped open ports necessary to my host environement|
    |`docker run -d --rm -p 8080:80 nginx`|Run an official Nginx image in a detached mode and mapped the port 8080 from my host to the port 80 in the container|
    |`docker run  -v pwd:pwd -it ubuntu ls`|The -v flag mounts the current working directory into the container and will list the contains of it|
        

1. `docker ps`

    The docker `ps` command allow to list the status of the containers.

    A container could be either stopped or running. When it finish to execute the process asked it will stop. 
    
    For example if you run the command `docker run -it ubuntu hostname` this will :
    - Pull the official ubuntu image from the registry
    - Start the container in the interactive mode `-it`
    - Execute the command : `hostname`
    - Stop

    ```
    $ docker run -it ubuntu hostname
    0d0af5005fc7
    ```

    If you run the command `docker ps -a` you should see :
    ```
     $ docker ps -a
    CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS                          PORTS               NAMES
    0d0af5005fc7        ubuntu              "hostname"          58 seconds ago      Exited (0) About a minute ago                       gifted_darwin
    ```

    > The `-a` allow you to list all the containers not only the running one

    We can notice few things here such as :
    - The status `Exited...` for our container
    - The name `gifted_darwin` randomly generated for our container, we can specify a custom one using the command `--name` explained in the previous section.
    - We can re execute our container using the command `docker start gifted_darwin`
    - We can run again the same command `docker run -it ubuntu hostname` and do a `docker ps -a`, we should see mow two containers exited.

1. `docker logs`

    The docker `logs` allow to fetch the console output from inside the container

    From our previous example, we can run `docker logs gifted_darwin`

    ```
    $ docker logs gifted_darwin
    0d0af5005fc7
    ```

    You can also stream the logs using the command `-f` and print in real time in your console the stdout of your container.

1. `docker rm`

    The docker `rm` command allow to remove a container.

    From the previous example, we can see that we have a container listed as exited in our environement, or maybe more if we run the same command `docker run -it ubuntu hostname` multiple time. If we want to do some clean and remove those executions from our environement we can use the command `docker rm`

    ```
    $ docker rm gifted_darwin
    gifted_darwin
    ```

    > You can either specify the **CONTAINER ID** or the **NAME** of the container to refer it


1. `docker images`

    This command allow us to list all the base images available in your environement.

    ```
    $ docker images
    REPOSITORY                                      TAG                 IMAGE ID            CREATED             SIZE
    ubuntu                                          latest              20c44cd7596f        2 days ago          123MB
    example-scratch                                 latest              32ff7b65f567        5 days ago          30.7MB
    node                                            8.9.1-slim          a6bb2cc1118f        11 days ago         230MB
    buildpack-deps                                  xenial              a27b6a8abd1c        2 weeks ago         644MB
    ```

    > You can manage your images by removing them using `docker rmi IMAGENAME` or pulling new one with `docker pull IMAGENAME`

#### Containerizing a simple application
#### Building and Pushing a Image

### Exercices



### Useful Links
* [What is Docker ?](https://www.docker.com/what-docker)
* [Docker for Mac](https://store.docker.com/editions/community/docker-ce-desktop-mac)
* [Docker for Windows](https://store.docker.com/editions/community/docker-ce-desktop-windows)
* [Docker for Ubuntu](https://store.docker.com/editions/community/docker-ce-server-ubuntu)
* [Docker for beginner](https://github.com/docker/labs/blob/master/beginner/readme.md)

### Expected Result

Doing a `kubectl describe pod <pod-name>` should show...