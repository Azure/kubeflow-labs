# GPUs And Kubernetes

## Prerequisites  
* [1 - Docker Basics](../1-docker)
* [2 - Kubernetes Basics and cluster created](../2-kubernetes)

## Summary

In this module you will learn how to:
* Create a Pod that is using GPU.
  * Requesting a GPU
  * Mounting the NVIDIA drivers into the container


## Important Note

If you created a cluster with CPU VMs only you won't be able to complete the exercises in this module, but it still contains valuable informations that you should read through nonetheless.

## How GPU works with Kubernetes

GPU support in K8s is still in it's early stage, and as such requires a bit of effort on your part to use.

While you don't need to do anything to access a CPU from inside your container (except specifying CPU request and limit optionnaly), getting access to the agent's  GPU is a little bit more tricky:  
* First, the drivers needs to be installed on the agent, otherwise this agent will not report the presence of GPU, and you won't be able to use it (this is already done for you in ACS/AKS/acs-engine).
* Then you need to explicitly ask for 1 or mutliple GPU(s) to be mounted into your container, otherwise you will simply not be able to access the GPU, even if is running on a GPU agent.
* Finally, and most importantly, you need to mount the drivers from the agent VM into your container, and update the relevant environment variables.

In Module 5, we will see how this process can be greatly simplified when using TensorFlow with `TfJob`, but for now, let's do it ourselves.


### Creating a container that can benefit from GPU

As a prerequesite for everything else, it is important to make sure that the container we are going to use actually knows what to do with a GPU.
For example TensorFlow needs to be installed with GPU support. CUDA and cuDNN also needs to be present.  
Thanksfully, most deep learning framework provide base images that are ready to use with GPU support, so we can use them as base image.

For example, TensorFlow has a lot of different images ready to use [https://hub.docker.com/r/tensorflow/tensorflow/tags/](https://hub.docker.com/r/tensorflow/tensorflow/tags/) such as:
* `tensorflow/tensorflow:1.4.0-gpu-py3` for GPU
* `tensorflow/tensorflow:1.4.0-py3` for CPU only

CNTK also has pre-built images with or without GPU [https://hub.docker.com/r/microsoft/cntk/tags/](https://hub.docker.com/r/microsoft/cntk/tags/):
* `microsoft/cntk:2.2-gpu-python3.5-cuda8.0-cudnn6.0` for GPU
* `microsoft/cntk:2.2-python3.5` for CPU only

Also what's important to note, is that most deep leanring frameworks images are built on top of the official [nvidia/cuda][https://hub.docker.com/r/nvidia/cuda/] image, which already comes with CUDA and cuDNN preinstalled, so you don't need to worry about installing them.


### Requesting GPU(s)

K8s has a concept of resource `requests` and `limits` allowing you to specify how much CPU, RAM and GPU should be reserved for a specific container.
By default, if no `limits` is specified for CPU or RAM on a container, K8s will schedule it on any node and run the container with unbounded CPU and memory limits.

> *To know more on K8s `requests` and `limits`, see [Managing Compute Resources for Containers](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/).*

However, things are different for GPUs. If no `limit` is defined for GPU, K8s will run the pod on any node (with or without GPU), and will not expose the GPU even if the node has one. So you need to explicitly set the `limit` to the exact number of GPUs that should be assigned to your container.  
Also, not that while you can request for a fraction of a CPU, you cannot request a franction of a GPU. One GPU can thus only be assigned to one container at a time.
The name for the GPU resource in K8s is `alpha.kubernetes.io/nvidia-gpu` for versions `1.8` and below and `nvidia.com/gpu` for versions > `1.9`. Note that currently only NVIDIA GPUs are supported.

To set the `limit` for GPU, you should provide a value to `spec.containers[].resources.limits.alpha.kubernetes.io/nvidia-gpu`, in YAML this would looks like:

```yaml
[...]
containers:
      - name: tensorflow
        image: tensorflow/tensorflow:latest-gpu
        resources:
          limits:
            alpha.kubernetes.io/nvidia-gpu: 1 
[...]
```

### Exposing the node's drivers into the container

Now for the tricky part.  
As stated earlier the NVIDIA drivers needs to be exposed (mounted) from the node into the container. This is a bit tricky since the location of the drivers can vary depending on the operating system of the node, as well as depending on how the drivers were installed.  
For ACS/AKS/acs-engine only Ubuntu nodes are supported so far, so it should be a consistent experience as long as your cluster was created with one of them.  

##### Drivers locations on the node

| Path | Purpose
|----|----|
|`/usr/lib/nvidia-384` | NVIDIA libraries |
|`/usr/lib/nvidia-384/bin`| NVIDIA binaries |
|`/usr/lib/x86_64-linux-gnu/libcuda.so.1` | CUDA Driver API library | 

> Note that the NVIDIA driver's version is `384` at the time of this writting, but the driver's location will change as the version change.

For each of the above paths we need to create a corresponding `Volume` and a `VolumeMount` to expose them into our container.  

> To understand how to configure `Volumes` and `VolumeMounts` take a look at [Volumes](https://kubernetes.io/docs/user-guide/walkthrough/#volumes) on the Kubernets documentation.

Finally we may also need to update some environment variable to reflect where the drivers were mounted in the container. Typically, `LD_LIBRARY_PATH` (responsible for referencing native code libraries) needs to be updated to reflect the location of both the NVIDIA libraries and CUDA Driver API library.

> See [Define Environment Variables for a Container](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/).


## Excercices

### 1. NVIDIA-SMI
In this first exercise we are simply going to schedule a `Job` that will run `nvidia-smi`, printing details about our GPU from inside the container and exit.
You don't need to build a custom image, instead, simply use the official `nvidia/cuda` docker image.

Your K8s YAML template should have the following caracteristics:
* It should be a `Job`
* It should be name `module4-ex1`
* It should request 1 GPU
* It should mount the drivers from the node into the container
* It should run the `nvidia-smi` executable

#### Useful Links
* [Microsoft Azure Container Service Engine - Using GPUs with Kubernetes](https://github.com/Azure/acs-engine/blob/master/docs/kubernetes/gpu.md)

#### Validation

Once you have created your Job with `kubectl create -f <template-path>:

```console
kubectl get pods -a
```
The `-a` arguments tells K8s to also report pods that are already completed. Since the container exits as soon as you nvidia-smi finishes executing, it might already be completed by the tome you execute the command.

```bash
NAME                 READY     STATUS        RESTARTS   AGE
module4-ex1-p40vx   0/1       Completed     0          20s
```

Let's look at the logs of our pod

```console 
kubectl logs <pod-name>
```
```bash
Wed Nov 29 23:43:03 2017
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 384.98                 Driver Version: 384.98                    |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  Tesla K80           Off  | 0000E322:00:00.0 Off |                    0 |
| N/A   39C    P0    70W / 149W |      0MiB / 11439MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                       GPU Memory |
|  GPU       PID   Type   Process name                             Usage      |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+
```
We can see that `nvidia-smi` has successfully detected a Tesla K80 with drivers version `384.98`.

#### Solution

<details>
<summary><strong>Solution (expand to see)</strong></summary>
<p>

```yaml
apiVersion: batch/v1
kind: Job # We want a Job
metadata:
  name: 4-nvidia-smi
spec:
  template:
    metadata:
      name: module4-ex1
    spec:
      restartPolicy: Never
      volumes: # Where the NVIDIA driver libraries and binaries are located on the host (note that libcuda is not needed to run nvidia-smi)
      - name: bin
        hostPath: 
          path: /usr/lib/nvidia-384/bin
      - name: lib
        hostPath: 
          path: /usr/lib/nvidia-384
      containers:
      - name: nvidia-smi
        image: nvidia/cuda # Which image to run        
        command: 
          - nvidia-smi
        resources:
          limits:
            alpha.kubernetes.io/nvidia-gpu: 1 # Requesting 1 GPU
        volumeMounts: # Where the NVIDIA driver libraries and binaries should be mounted inside our container
        - name: bin
          mountPath: /usr/local/nvidia/bin
        - name: lib
          mountPath: /usr/lib/nvidia
```
</p>
</details>

### 2. Running TensorFlow with GPU

In module 1 and 2, we first created a Docker image for our MNIST classifier and then ran a training on Kubernetes.  
However, this training only used CPU. Let's make things much faster by accelerating our training with GPU.

You'll find the code and the `Dockerfile` under [`./src`](./src).

For this excercise, your tasks are to:
* Modify our `Dockerfile` to use a base image compatible with GPU, such as `tensorflow/tensorflow:1.4.0-gpu`
* Build and push this new image under a new tag, such as `${DOCKER_USERNAME}/tf-mnist:gpu`
* Modify the [template we built in module 2](2-kubernetes/training.yaml) to add a GPU `limit` and mount the drivers libraries.
* Deploy this new template.

### Validation

Once you deployed your template, take a look at the logs of your pod:

```console
kubectl logs <pod-name>
```
And you should see that your GPU is correctly detected and used by TensorFlow ( `[...] Found device 0 with properties: name: Tesla K80 [...]`)

```bash
2017-11-30 00:59:54.053227: I tensorflow/core/platform/cpu_feature_guard.cc:137] Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.1 SSE4.2 AVX AVX2 FMA
2017-11-30 01:00:03.274198: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1030] Found device 0 with properties:
name: Tesla K80 major: 3 minor: 7 memoryClockRate(GHz): 0.8235
pciBusID: b2de:00:00.0
totalMemory: 11.17GiB freeMemory: 11.10GiB
2017-11-30 01:00:03.274238: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1120] Creating TensorFlow device (/device:GPU:0) -> (device: 0, name: Tesla K80, pci bus id: b2de:00:00.0, compute capability: 3.7)
2017-11-30 01:00:08.000884: I tensorflow/stream_executor/dso_loader.cc:139] successfully opened CUDA library libcupti.so.8.0 locally
Successfully downloaded train-images-idx3-ubyte.gz 9912422 bytes.
Extracting /tmp/tensorflow/input_data/train-images-idx3-ubyte.gz
Successfully downloaded train-labels-idx1-ubyte.gz 28881 bytes.
Extracting /tmp/tensorflow/input_data/train-labels-idx1-ubyte.gz
Successfully downloaded t10k-images-idx3-ubyte.gz 1648877 bytes.
Extracting /tmp/tensorflow/input_data/t10k-images-idx3-ubyte.gz
Successfully downloaded t10k-labels-idx1-ubyte.gz 4542 bytes.
Extracting /tmp/tensorflow/input_data/t10k-labels-idx1-ubyte.gz
Accuracy at step 0: 0.1245
Accuracy at step 10: 0.6664
Accuracy at step 20: 0.8227
Accuracy at step 30: 0.8657
Accuracy at step 40: 0.8815
Accuracy at step 50: 0.892
Accuracy at step 60: 0.9068
[...]
```


### Solution


<details>
<summary><strong>Solution (expand to see)</strong></summary>
<p>

First we need to modify the `Dockerfile`.
We just need to change the tag of the TensorFlow base image to be one that support GPU:

```dockerfile
FROM tensorflow/tensorflow:1.4.0-gpu
COPY main.py /app/main.py

ENTRYPOINT ["python", "/app/main.py"]
```

Then we can create our Job template:

```yaml
apiVersion: batch/v1
kind: Job # Our training should be a Job since it is supposed to terminate at some point
metadata:
  name: module4-ex2 # Name of our job
spec:
  template: # Template of the Pod that is going to be run by the Job
    metadata:
      name: mnist-pod # Name of the pod
    spec:
      containers: # List of containers that should run inside the pod, in our case there is only one.
      - name: tensorflow
        image: wbuchwalter/tf-mnist:gpu # The image to run, you can replace by your own.
        args: ["--max_steps", "500"] # Optional arguments to pass to our command. By default the command is defined by ENTRYPOINT in the Dockerfile
        resources:
          limits:
            alpha.kubernetes.io/nvidia-gpu: 1
        volumeMounts: # Where the drivers should be mounted in the container
        - name: lib
          mountPath: /usr/local/nvidia/lib64
        - name: libcuda
          mountPath: /usr/lib/x86_64-linux-gnu/libcuda.so.1
      restartPolicy: OnFailure
      volumes: # Where the drivers are located on the node
        - name: lib
          hostPath: 
            path: /usr/lib/nvidia-384
        - name: libcuda
          hostPath:
            path: /usr/lib/x86_64-linux-gnu/libcuda.so.1
```

And deploy it with 

```console
kubectl create -f <template-path>
```

</p>
</details>

## Next Step
[5 - TfJob](../5-tfjob/README.md)
