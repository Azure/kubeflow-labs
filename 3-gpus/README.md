# GPUs And Kubernetes

### Prerequisites  
* [Docker Basics](../1-docker)
* [Kubernetes Basics and cluster created](../2-kubernetes)

> **Note**: If you created a cluster without GPU agent you won't be able to complete the exercices in this module, but it still contains valuable informations.

### Summary

In this tutorial you will learn how to:
* Create a Pod that is using GPU.
  * Requesting a GPU
  * Mounting the NVIDIA drivers into the container

### GPUs and Kubernetes

GPU support in K8s is still in it's early stage, and as such requires a bit of effort on your part to use.

While you don't need to do anything to access a CPU from inside your container (except specifying CPU request and limit optionnaly), getting access to the agent's  GPU is a little bit more tricky:  
* First, the drivers needs to be installed on the agent, otherwise this agent will not report the presence of GPU, and you won't be able to use it (this is already done for you in ACS/AKS/acs-engine).
* Then you need to explicitly ask for 1 or mutliple GPU(s) to be mounted into your container, otherwise you will simply not be able to access the GPU, even if is running on a GPU agent.
* Finally, and most importantly, you need to mount the drivers from the agent VM into your container, and update the relevant environment variables.

In Module 5, we will see how this process can be greatly simplified when using TensorFlow with `TfJob`, but for now, let's do it ourselves.


LD_LIBRARY_PATH

tensorflow vs Tensorflow-gpu (includes CUDNN etc.)

### Excercices and Useful Links

1. Create a 


### Useful Links
* [Microsoft Azure Container Service Engine - Using GPUs with Kubernetes](https://github.com/Azure/acs-engine/blob/master/docs/kubernetes/gpu.md)

### Expected Result

Doing a `kubectl describe pod <pod-name>` should show...