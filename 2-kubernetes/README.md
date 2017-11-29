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

### Creating a Kubernetes Object

When you create an object in Kubernetes, you must provide the object spec that describes its desired state, as well as some basic information about the object (such as a name) to the Kubernetes API either directly or via the `kubectl` command-line interface. The request must include the information as JSON in the request body. Most often, you can provide the information to `kubectl` in a .yaml file. `kubectl` then converts the information to JSON when making the API request. In the next few sections, we will be using various yaml files to describe the Kubernetes objects we want to deploy to our Kubernetes cluster.

For example, the `.yaml` file shown below includes the required fields and object spec for a Kubernetes Deployment. A Kubernetes Deployment is an object that can represent an application running on your cluster. In the example below, the Deployment spec describes the desired state of three replicas of the nginx application to be running. When you create the Deployment, the Kubernetes system reads the Deployment spec and starts three instances of your desired application, updating the status to match your spec.

```yaml
apiVersion: apps/v1beta2 # for versions before 1.8.0 use apps/v1beta1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.7.9
        ports:
        - containerPort: 80
```

To create all the objects described in a Deployment using a `.yaml` file like the one above in your own Kubernetes cluster, run the following command using the `kubectl` command-line interface:

```
$ kubectl create -f https://k8s.io/docs/user-guide/nginx-deployment.yaml
```

## Provisioning a Kubernetes cluster on Azure

There are multiple ways to provision a Kubernetes (K8s) on Azure:
* ACS
* AKS
* acs-engine

AKS is currently still in preview and acs-engine is a bit more complex to setup, so we advice you to create your cluster using ACS.

We are going to create a Linux-based K8s cluster.
You can either create the cluster using the portal, or using Azure-CLI (`az`).

### A Note on GPUs with Kubernetes

As of this writing, GPUs are still in preview with ACS.  
You can deploy an ACS cluster with GPU VMs (such as `Standard_NC6`) in `uswest2` or `uksouth` but you should be aware of some pitfalls:
* Deploying a GPU cluster takes longer than a CPU cluster (about 10-15 minutes more) because the NVIDIA drivers need to be installed as well.
* Since this is a preview, you might hit capacity issues if the location you chose does not have enough GPUs available to accomodate you.

**Unless you are already pretty familiar with docker and Kubernetes, we recommend that you create a cluster with CPU VMs to save some time.**
Only module 3 has an excercise which is specific for GPU VMs, all other modules can be followed on either CPU or GPU clusters.

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
az acs create --agent-vm-size <AGENT_SIZE> --resource-group <RG> --name <NAME> 
--orchestrator-type Kubernetes --agent-count <AGENT_COUNT> 
--location <LOCATION> --generate-ssh-keys
```

With:  
  
| Parameter | Description |
| --- | --- | 
| AGENT_SIZE | The size of K8s's agent VM. `Standard_D2_v2` is enough for this workshop. |
| RG | Name of the resource group that was created in the previous step. |
| NAME | Name of the ACS resource (can be whatever you want). | 
| AGENT_COUNT | The number of agents (virtual machines) that you want in your cluster. 2 or 3 is recommended to play with hyper-parameter tuning and distributed TensorFlow | 
| LOCATION | Same location that was specified for the resource group creation. |

The command should take a few minutes to complete (longer if you chose GPU VMs). Once it is done, the output should be a JSON object indicating among other things the `provisioningState`:
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
az acs kubernetes get-credentials --name <NAME> --resource-group <RG>
```

Where `NAME` and `RG` should be the same values as for the cluster creation.

## Validation

Once you are done with the cluster creation, and downloaded the `kubeconfig` file, running the following command:

```console
kubectl get nodes
```

Should yield an output similar to this one:
```
NAME                    STATUS    AGE       VERSION
k8s-agent-ef2b999d-0    Ready     9d        v1.7.7
k8s-agent-ef2b999d-1    Ready     9d        v1.7.7
k8s-agent-ef2b999d-2    Ready     9d        v1.7.7
k8s-master-ef2b999d-0   Ready     9d        v1.7.7
```

If you provisioned GPU VM, describing one of the node should indicate the presence of GPU(s) on the node:
```console
> kubectl describe node <NODE_NAME>

[...]
Capacity:
 alpha.kubernetes.io/nvidia-gpu:	1
[...]
 ```

## Next Step
[Module 3: GPUs](../3-gpus/README.md)
