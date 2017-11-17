# Kubernetes

### Prerequisites  
* [Docker Basics](../1-docker/README.md)

### Summary

In this module you will learn :
* The basic concepts of Kubernetes
* How to create a Kubernetes cluster on Azure

> *Important* : Kubernetes is very often abbreviated to **K8s**. This is the name we are going to use in this workshop.


## Provisioning a Kubernetes cluster

There are multiple ways to provision a Kubernetes (K8s) on Azure:
* ACS
* AKS
* acs-engine

AKS is currently still in preview and acs-engine is a bit more complex to setup, so we advice you to create your cluster using ACS.

We are going to create a Linux-based K8s cluster.
You can either create the cluster using the portal, or using Azure-CLI (`az`).

### With the CLI

#### Creating a resource group
```console
az group create --name <RESOURCE_GROUP_NAME> --location <LOCATION>
```  

With:  
  
| Parameter | Description |
| --- | --- | 
| RESOURCE_GROUP_NAME | Name of the resource group where the cluster will be deployed.  |
| LOCATION | Name of the region where the cluster should be deployed. If you are going to use GPUs, make sure you target one of the region with GPU availability (such as `southcentralus`, `westus`, `eastus` etc.). |


#### Creating the cluster  
```console
az acs create --agent-vm-size <AGENT_SIZE> --resource-group <RG> --name <NAME> 
--orchestrator-type Kubernetes --agent-count <AGENT_COUNT> 
--location <LOCATION> --generate_ssh_keys True
```

With:  
  
| Parameter | Description |
| --- | --- | 
| AGENT_SIZE | The size of K8s's agent VM. For this workshop use `Standard_NC6` if you want GPUs or `Standard_D2_v2` for CPU only. |
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

If you provisioned GPU VM, describing one of the node with:
```console
kubectl describe node <NODE_NAME>
```

Should indicate the presence of GPU(s) on the node:
```
[...]
Capacity:
 alpha.kubernetes.io/nvidia-gpu:	1
[...]
 ```


## Next Step
[Module 3: GPUs](../3-gpus/README.md)
