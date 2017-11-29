# Docker

### Summary

In this section you will learn about:
* Running Docker locally
* Basics of Docker
* Containerizing a simple application
* Building and Pushing an Image



### Basics of Docker and Containers

Docker has a very well structured six-part tutorial. 
While for this workshop you don't need to go through all of them, part 1 and 2 are required:
* [Get Started, Part 1: Orientation and setup](https://docs.docker.com/get-started)
* [Get Started, Part 2: Containers](https://docs.docker.com/get-started/part2/)

By the end of Part 2, you should have a simple container up and running, and understand the basic concepts of a container.

#### Additional Important Docker Command

Here a few other docker commands that are important to be aware of for the rest of this workshop:

1. `docker ps`

    The docker `ps` command allows to list the status of the containers.

    A container could be either stopped or running. When it finishes to execute the process, it will stop. 
    
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

    > The `-a` allows you to list all the containers, not just the one that is running 

    We can notice a few things here such as :
    - The status `Exited...` for our container
    - The name `gifted_darwin` randomly generated for our container, we can specify a custom one using the command `--name` explained in the previous section.
    - We can re-execute our container using the command `docker start gifted_darwin`
    - We can run the command `docker run -it ubuntu hostname` again and do a `docker ps -a`; we should see how two containers exited.

1. `docker logs`

    The docker `logs` allow to fetch the console output from inside the container

    From our previous example, we can run `docker logs gifted_darwin`

    ```
    $ docker logs gifted_darwin
    0d0af5005fc7
    ```

    You can also stream the logs using the command `-f` and print in real time in your console the stdout of your container.

1. `docker rm`

    The docker `rm` command allows to remove a container.

    From the previous example, we can see that we have a container listed as exited in our environement, or maybe more if we run the same command `docker run -it ubuntu hostname` multiple times. If we want to do some cleaning and remove those executions from our environement we can use the command `docker rm`

    ```
    $ docker rm gifted_darwin
    gifted_darwin
    ```

    > You can either specify the **CONTAINER ID** or the **NAME** of the container to refer to it


1. `docker images`

    This command allows us to list all the base images available in the environement.

    ```
    $ docker images
    REPOSITORY                                      TAG                 IMAGE ID            CREATED             SIZE
    ubuntu                                          latest              20c44cd7596f        2 days ago          123MB
    example-scratch                                 latest              32ff7b65f567        5 days ago          30.7MB
    node                                            8.9.1-slim          a6bb2cc1118f        11 days ago         230MB
    buildpack-deps                                  xenial              a27b6a8abd1c        2 weeks ago         644MB
    ```

    > You can manage your images by removing them using `docker rmi IMAGENAME` or pulling a new one with `docker pull IMAGENAME`

### Containerizing a TensorFlow model

Now that we understand the basics of Docker, let's containerize our first TensorFlow model that we will reuse in the following modules.  
Our first model will be a very simple MNIST classifier. You can see the source code in `./src/main.py`.    
As you can see there is nothing specific to containers in this code, you can run this script directly on your laptop or on a VM.

Now to have this run in a container, we need to build an image containing this code and it's dependencies.  
As you saw in the tutorial, we will use a `Dockerfile` to do this.

Here is the (very simple) `Dockerfile` that we are going to use for this model (located in `./src/Dockerfile`):

```dockerfile
FROM tensorflow/tensorflow:1.4.0
COPY main.py /app/main.py

ENTRYPOINT ["python", "/app/main.py"]
```

As you can see, we are not building a new image from scratch, instead we are using a base image from TensorFlow. Indeed, TensorFlow has a bunch of base images that you can start with.
You can see the full list here: https://hub.docker.com/r/tensorflow/tensorflow/tags/.

What is important to note is that different tags need to be used depending on if you want to use GPU or not.  
For example, if you wanted to run your model with TensorFlow 1.4.0 and CPU only, you would use `tensorflow/tensorflow:1.4.0`.  
If instead you wanted to use GPU, you would start from `tensorflow/tensorflow:1.4.0-gpu`.

The two other instructions are pretty straightforward, first we copy our script into the container, and then we set this script as the entry point for our container, so that any argument passed to our container would actually get passed to our script.

#### Building the image

> If you don't already have a Docker account, see [Log in with your Docker ID](https://docs.docker.com/get-started/part2/#log-in-with-your-docker-id).

The next step is to build our image to be able to run it using docker. For that, we will use the command `docker build`.

From the `./src` repository, we can build the image with

```console
docker build -t ${DOCKER_USERNAME}/tf-mnist .
```
> Reminder: the `-t` argument allows to **tag** the image with a specific name.  

`${DOCKER_USERNAME}` should be your Docker username that you use to connect to Docker Hub.

The output from this command should look like this:

```
Sending build context to Docker daemon  11.26kB
Step 1/3 : FROM tensorflow/tensorflow:1.4.0
 ---> a61a91cc0d1b
Step 2/3 : COPY main.py /app/main.py
 ---> b264d6e9a5ef
Removing intermediate container fe8128425296
Step 3/3 : ENTRYPOINT python /app/main.py
 ---> Running in 7acb7aac7a9f
 ---> 92c7ed17916b
Removing intermediate container 7acb7aac7a9f
Successfully built 92c7ed17916b
Successfully tagged wbuchwalter/tf-mnist:latest
```
Let's analyse this image full name:
* `wbuchwalter` is the name of the repository (same as your docker hub username), this is where we can find the image
* `tf-mnist` is the name of the image itself
* `latest` is the tag. `latest` is the default tag if you don't specify any. Tags are usually used to denote different versions or flavors of a same image. For example you could have a tag `v1` and `v2` to denote different versions, or `cpu` and `gpu` to denote what hardware it can run on.  

When you have the successfully built message, you should now be able to see if your image is locally available with the command `docker images` described earlier.

#### Running the image  

Now we can try to run it locally using the `docker run` command.   
By default the model will run 1000 training steps which can take a few minutes on a laptop. Let's reduce this number to 100 with the `--max_steps` argument. 

```console
docker run -it ${DOCKER_USERNAME}/tf-mnist --max_steps 100
```

If everything is okay you should see the model training:

```
Successfully downloaded train-images-idx3-ubyte.gz 9912422 bytes.
Extracting /tmp/tensorflow/input_data/train-images-idx3-ubyte.gz
Successfully downloaded train-labels-idx1-ubyte.gz 28881 bytes.
Extracting /tmp/tensorflow/input_data/train-labels-idx1-ubyte.gz
Successfully downloaded t10k-images-idx3-ubyte.gz 1648877 bytes.
Extracting /tmp/tensorflow/input_data/t10k-images-idx3-ubyte.gz
Successfully downloaded t10k-labels-idx1-ubyte.gz 4542 bytes.
Extracting /tmp/tensorflow/input_data/t10k-labels-idx1-ubyte.gz
2017-11-29 18:32:41.992194: I tensorflow/core/platform/cpu_feature_guard.cc:137] Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.1 SSE4.2 AVX AVX2 FMA
Accuracy at step 0: 0.1292
Accuracy at step 10: 0.7198
Accuracy at step 20: 0.834
Accuracy at step 30: 0.8698
Accuracy at step 40: 0.8783
Accuracy at step 50: 0.8968
Accuracy at step 60: 0.9023
Accuracy at step 70: 0.9059
Accuracy at step 80: 0.9084
Accuracy at step 90: 0.9154
Adding run metadata for 99
```

You can kill the process and exit the container at any time with `ctrl + c`.

### Running the image with GPU

**Currently, running docker containers with GPU is only supported on Linux.**

First install [nvidia-docker](https://github.com/NVIDIA/nvidia-docker).  

You also need to make sure the image you are going to use is optimized for GPU.  
In our example you need to modify the `Dockerfile` to use a TensorFlow image built for GPU:

```dockerfile 
FROM tensorflow/tensorflow:1.4.0-gpu
COPY main.py /app/main.py

ENTRYPOINT ["python", "/app/main.py"]
```

Then simply rebuild the image with a new tag (you can use docker or nvidia-docker interchangeably for any command except run):

```console
docker build -t ${DOCKER_USERNAME}/tf-mnist:gpu
```

Finally run the container with nvidia-docker:

```console
nvidia-docker run -it ${DOCKER_USERNAME}/tf-mnist:gpu
```

#### Publish the Image

Our image is now built and running locally, but what about sharing it to be able to use it from anywhere by anyone?  
Most importantly we want to be able to reuse this image on the Kubernetes cluster we are going to create in module 2.
So let's push our image to Docker Hub:

```console
docker push ${DOCKER_USERNAME}/tf-mnist
```

If this comand doesn't look familiar to you, make sure you went through part 1 and 2 of Docker's tutorial, and more precisely: [Tutorial - Share your image](https://docs.docker.com/get-started/part2/#share-your-image)


### Useful Links
* [What is Docker ?](https://www.docker.com/what-docker)
* [Docker for beginner](https://github.com/docker/labs/blob/master/beginner/readme.md)


## Next Step
[2 - Kubernetes](../2-kubernetes/README.md)