# GPUs And Kubernetes

## Prerequisites  
* [1 - Docker Basics](../1-docker)
* [2 - Kubernetes Basics and cluster created](../2-kubernetes)

## Summary

In this module you will learn how to:
* Create a Pod that is using GPU.
  * Requesting a GPU
  * Mounting the NVIDIA drivers into the container

> **Note**: If you created a cluster without GPU agent you won't be able to complete the exercices in this module, but it still contains valuable informations.

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

K8s has a concept of resource `requests` allowing you to specify how much CPU, RAM and GPU should be reserved for a specific container, and `limits` allowing you to specify the maximum amount of resources a container should consume.  
By default, if no `requests` and `limits` is specified for CPU or RAM on a container, K8s will schedule it on any node and run the container with unbounded CPU and memory limits.

> *To know more on K8s `requests` and `limits`, see [Managing Compute Resources for Containers](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/).*

However, things are different for GPUs. If no GPU is requested, K8s will run the pod on any node (with or without GPU), and will not expose the GPU even if the node has one. So you need to explicitly request the exact number of GPUs that should be assigned to your container.  
Also, not that while you can request for a fraction of a CPU, you cannot request a franction of a GPU. One GPU can thus only be assigned to one container at a time.
The name for the GPU resource in K8s is `alpha.kubernetes.io/nvidia-gpu` for versions `1.8` and below and `nvidia.com/gpu` for versions > `1.9`. Note that currently only NVIDIA GPUs are supported.

To request GPU, you should provide a value to `spec.containers[].resources.requests.alpha.kubernetes.io/nvidia-gpu`, in YAML this would looks like:

```yaml
[...]
containers:
      - name: tensorflow
        image: tensorflow/tensorflow:latest-gpu
        resources:
          requests:
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


## Excercices and Useful Links

### 1. NVIDIA-SMI
In this first exercice we are simply going to schedule a `Job` that will run `nvidia-smi`, printing details about our GPU from inside the container and exit.
You don't need to build a custom image, instead, simply use the official `nvidia/cuda` docker image.

Your K8s YAML template should have the following caracteristics:
* It should be a `Job`
* It should request 1 GPU
* It should mount the drivers from the node into the container
* It should run `nvidia-smi`

#### Useful Links
* [Microsoft Azure Container Service Engine - Using GPUs with Kubernetes](https://github.com/Azure/acs-engine/blob/master/docs/kubernetes/gpu.md)

#### Validation

Doing a `kubectl logs <pod-name>` should show...

<details>
<summary><strong>Solution (expand to see)</strong></summary>
<p>

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: nvidia-smi
spec:
  template:
    metadata:
      name: nvidia-smi
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
          - nvidia-smi # The command to run when the container starts
        resources:
          requests:
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

## Next Step
[4 - Helm](../4-helm/README.md)