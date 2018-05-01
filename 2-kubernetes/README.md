# Kubernetes

### Prerequisites  
* [Docker Basics](../1-docker/README.md)

### Summary

In this module you will learn:
* The basic concepts of Kubernetes
* How to create a Kubernetes cluster on Azure

> *Important* : Kubernetes is very often abbreviated to **K8s**. This is the name we are going to use in this workshop.

## The basic concepts of Kubernetes

[Kubernetes](https://kubernetes.io/) is an open-source technology that makes it easier to automate deployment, scale, and manage containerized applications in a clustered environment. The ability to use GPUs with Kubernetes allows the clusters to facilitate running frequent experimentations, using it for high-performing serving, and auto-scaling of deep learning models, and much more. 

### Overview

Kubernetes is a system for managing containerized applications across a cluster of nodes. To work with Kubernetes, you use Kubernetes API objects to describe your cluster’s desired state: what applications or other workloads you want to run, what container images they use, the number of replicas, what network and disk resources you want to make available, and more. You set your desired state by creating objects using the Kubernetes API. Once you’ve set your desired state, the Kubernetes Control Plane works to make the cluster’s current state match the desired state. To do so, Kubernetes performs a variety of tasks automatically, such as starting or restarting containers, scaling the number of replicas of a given application, and more.

### Kubernetes Master

The Kubernetes master is responsible for maintaining the desired state for your cluster. When you interact with Kubernetes, such as by using the kubectl command-line interface, you’re communicating with your cluster’s Kubernetes master. These master services can be installed on a single machine, or distributed across multiple machines. In the following [Provisioning a Kubernetes cluster on Azure](#provisioning-a-kubernetes-cluster-on-azure) section, we will be creating a Kubernetes cluster with 1 master.

### Kubernetes Nodes

The worker nodes communicate with the master components, configure the networking for containers, and run the actual workloads assigned to them. In the following [Provisioning a Kubernetes cluster on Azure](#provisioning-a-kubernetes-cluster-on-azure) section, we will be creating a Kubernetes cluster with 3 worker nodes.

### Kubernetes Objects

Kubernetes contains a number of abstractions that represent the state of your system: deployed containerized applications and workloads, their associated network and disk resources, and other information about what your cluster is doing. A Kubernetes object is a "record of intent" – once you create the object, the Kubernetes system will constantly work to ensure that object exists. By creating an object, you’re telling the Kubernetes system your cluster’s desired state.

The basic Kubernetes objects include:
* Pod - the smallest and simplest unit in the Kubernetes object model that you create or deploy. A Pod encapsulates an application container (or multiple containers), storage resources, a unique network IP, and options that govern how the container(s) should run.
* Service - an abstraction which defines a logical set of Pods and a policy by which to access them.
* Volume - an abstraction which allows data to be preserved across container restarts and allows data to be shared between different containers.
* Namespace - a way to divide a physical cluster resources into multiple virtual clusters between multiple users.
* Deployment - Manages pods and ensures a certain number of them are running. This is typically used to deploy pods that should always be up, such as a web server.
* Job - A job creates one or more pods and ensures that a specified number of them successfully terminate. In other words, we use Job to run a task that finishes at some point, such as training a model.

### Creating a Kubernetes Object

When you create an object in Kubernetes, you must provide the object specifications that describes its desired state, as well as some basic information about the object (such as a name) to the Kubernetes API either directly or via the `kubectl` command-line interface. Usually, you will provide the information to `kubectl` in a .yaml file. `kubectl` then converts the information to JSON when making the API request. In the next few sections, we will be using various yaml files to describe the Kubernetes objects we want to deploy to our Kubernetes cluster.

For example, the `.yaml` file shown below includes the required fields and object spec for a Kubernetes Deployment. A Kubernetes Deployment is an object that can represent an application running on your cluster. In the example below, the Deployment spec describes the desired state of three replicas of the nginx application to be running. When you create the Deployment, the Kubernetes system reads the Deployment spec and starts three instances of your desired application, updating the status to match your spec.

```yaml
apiVersion: apps/v1beta2 # Kubernetes API version for the object
kind: Deployment # The type of object described by this YAML, here a Deployment
metadata:
  name: nginx-deployment # Name of the deployment
spec: # Actual specifications of this deployment
  replicas: 3 # Number of replicas (instances) for this deployment. 1 replica = 1 pod
  template: 
    metadata:
      labels:
        app: nginx
    spec: # Specification for the Pod 
      containers: # These are the containers running inside our Pod, in our case a single one
      - name: nginx # Name of this container
        image: nginx:1.7.9 # Image to run
        ports: # Ports to expose
        - containerPort: 80
```

To create all the objects described in a Deployment using a `.yaml` file like the one above in your own Kubernetes cluster you can use Kubernetes' CLI (`kubectl`). 
We will be creating a deployment in the exercise toward the end of this module, but first we need a cluster.

## Provisioning a Kubernetes cluster on Azure

We are going to use AKS to create a GPU-enabled Kubernetes cluster.
You could also use [acs-engine](https://github.com/Azure/acs-engine) if you prefer, this guide will assume you are using aks.


### A Note on GPUs with Kubernetes

As of this writing, GPUs are available for AKS in the `eastus` and `westeurope` regions. If you wants more options you may want to use acs-engine for more flexibility.

### With the CLI

#### Creating a resource group
```console
az group create --name <RESOURCE_GROUP_NAME> --location <LOCATION>
```  

With:  
  
| Parameter | Description |
| --- | --- | 
| RESOURCE_GROUP_NAME | Name of the resource group where the cluster will be deployed.  |
| LOCATION | Name of the region where the cluster should be deployed. |

#### Creating the cluster  
```console
az aks create --agent-vm-size <AGENT_SIZE> --resource-group <RG> --name <NAME> 
--agent-count <AGENT_COUNT> --kubernetes-version 1.9.6 --location <LOCATION> --generate-ssh-keys
```

> Note : The kubernetes verion could change depending where you are deploying your cluster. You can get more informations running the `az aks get-versions` command.

With:  
  
| Parameter | Description |
| --- | --- | 
| AGENT_SIZE | The size of K8s's agent VM. Choose `Standard_NC6` for GPUs or `Standard_D2_v2` if you just want CPUs. |
| RG | Name of the resource group that was created in the previous step. |
| NAME | Name of the ACS resource (can be whatever you want). | 
| AGENT_COUNT | The number of agents (virtual machines) that you want in your cluster. 2 or 3 is recommended to play with hyper-parameter tuning and distributed TensorFlow | 
| LOCATION | Same location that was specified for the resource group creation. |

The command should take a few minutes to complete. Once it is done, the output should be a JSON object indicating among other things the `provisioningState`:
```
{
  [...]
  "provisioningState": "Succeeded",
  [...]
}
```

#### Getting the `kubeconfig` file

The `kubeconfig` file is a configuration file that will allow Kubernetes's CLI (`kubectl`) to know how to talk to our cluster.
To download the `kubeconfig` file from the cluster we just created, run:

```console
az aks get-credentials --name <NAME> --resource-group <RG>
```

Where `NAME` and `RG` should be the same values as for the cluster creation.

##### Validation

Once you are done with the cluster creation, and downloaded the `kubeconfig` file, running the following command:

```console
kubectl get nodes
```

Should yield an output similar to this one:
```
NAME                       STATUS    ROLES     AGE       VERSION
aks-nodepool1-42640332-0   Ready     agent     1h        v1.9.6
aks-nodepool1-42640332-1   Ready     agent     1h        v1.9.6
aks-nodepool1-42640332-2   Ready     agent     1h        v1.9.6
```

If you provisioned GPU VM, describing one of the node should indicate the presence of GPU(s) on the node:
```console
> kubectl describe node <NODE_NAME>

[...]
Capacity:
 alpha.kubernetes.io/nvidia-gpu:	1
[...]
 ```

## Exercise

### Running our Model on Kubernetes

> Note: If you didn't complete the exercise in module 1, you can use `wbuchwalter/tf-mnist` image for this exercise.

In module 1, we created an image for our MNIST classifier, ran a small training locally and pushed this image to Docker Hub.  
Since we now have a running Kubernetes cluster, let's run our training on it!

First, we need to create a YAML template to define what we want to deploy.
We want our deployment to have a few characteristics:
* It should be a `Job` since we expect the training to finish successfully after some time.
* It should run the image you created in module 1 (or `wbuchwalter/tf-mnist` if you skipped this module).
* The `Job` should be named `2-mnist-training`.
* We want our training to run for `500` steps.
* We want our training to use 1 GPU

Here is what this would look like in YAML format:

```yaml
apiVersion: batch/v1
kind: Job # Our training should be a Job since it is supposed to terminate at some point
metadata:
  name: module2-ex1 # Name of our job
spec:
  template: # Template of the Pod that is going to be run by the Job
    metadata:
      name: module2-ex1 # Name of the pod
    spec:
      containers: # List of containers that should run inside the pod, in our case there is only one.
      - name: tensorflow
        image: ${DOCKER_USERNAME}/tf-mnist:gpu # The image to run, you can replace by your own.
        args: ["--max_steps", "500"] # Optional arguments to pass to our command. By default the command is defined by ENTRYPOINT in the Dockerfile
        resources:
          limits:
            alpha.kubernetes.io/nvidia-gpu: 1 # We ask Kubernetes to assign 1 GPU to this container 
      restartPolicy: OnFailure # restart the pod if it fails
```

Save this template somewhere and deploy it with:

```console
kubectl create -f <path-to-your-template>
```

#### Validation

After deploying the template,

```console
kubectl get job
```

Should show your new job:

```bash
NAME                             DESIRED   SUCCESSFUL   AGE
module2-ex1                      1         0            1m
```

Looking at the Pods:
```console
kubectl get pods
````
You should see your training running
```bash
NAME                                      READY     STATUS      RESTARTS   AGE
module2-ex1-c5b8q                      1/1       Runing      0          1m
```

Finally you can look at the logs of your pod with:

```console
kubectl logs <pod-name>
```
> Be careful to use the Pod name (from `kubectl get pods`) not the Job name.

And you should see the training happening

```bash
2017-11-29 21:49:16.462292: I tensorflow/core/platform/cpu_feature_guard.cc:137] Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.1 SSE4.2 AVX
Successfully downloaded train-images-idx3-ubyte.gz 9912422 bytes.
Extracting /tmp/tensorflow/input_data/train-images-idx3-ubyte.gz
Successfully downloaded train-labels-idx1-ubyte.gz 28881 bytes.
Extracting /tmp/tensorflow/input_data/train-labels-idx1-ubyte.gz
Successfully downloaded t10k-images-idx3-ubyte.gz 1648877 bytes.
Extracting /tmp/tensorflow/input_data/t10k-images-idx3-ubyte.gz
Successfully downloaded t10k-labels-idx1-ubyte.gz 4542 bytes.
Extracting /tmp/tensorflow/input_data/t10k-labels-idx1-ubyte.gz
Accuracy at step 0: 0.1285
Accuracy at step 10: 0.674
Accuracy at step 20: 0.8065
Accuracy at step 30: 0.8606
Accuracy at step 40: 0.8759
Accuracy at step 50: 0.888
[...]
```

After a few minutes, looking again at the Job should show that it has completed successfully:
```console
kubectl get job
```

```bash
NAME                           DESIRED   SUCCESSFUL   AGE
module2-ex1                    1         1            3m
```

## Next Step

Currently our training doesn't do anything interesting. We are not even saving the model and summaries anywhere, but don't worry we are going to dive into this starting in Module 4.

[Module 3: Helm](../3-helm/README.md)

