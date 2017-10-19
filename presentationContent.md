# Presentation Content 
 
ACS and TfJob are moving rapidly, so this content might change a bit depending on the availability of new features.  
We expect AKS to be out and supporting GPUs.  
If not we will have to fallback on acs-engine and remove some content to stay in the 2 hours.


## Prerequisite
  * Docker installed and working
  * Azure cli (az) installed
  * Very basic knowledge of Docker is definitly a plus, but not required

## Summary

**Part 2 to 8 will be delived interactively through a GitHub repository and markdown documentation so that different attendees can go at different paces**

1. Introduction (PowerPoint) - *10 min*
   - Current typical workflow in ML
   - Shortcomings of this Workflow (data/model versioning, slow training, scalability etc.)
   - How containers and kubernetes can help
1. Other MS tools (PowerPoint) - *10 min included from the introduction time*
   - Azure Batch AI training
   - Vienna
1. Introduction to Containers and Docker *20 min*
   - Basics of containers
     - The goal here is to bring everyone to a level where they can understand what is happening in the rest of the session with Kubernetes, and pick their interest in containers so that they can learn more about them by themselves.
   - Why containers are useful (reproducibility, scalability, packaging...)
   - DockerHub
     - **P**: Creating an account to host our images
     - Discovering existing images (Tensorflow, CNTK etc.) and their different version (tags)
1. Introduction to Kubernetes *25 min*
   - What is an orchestrator, why we need them
   - Fundamental concepts of K8s
     - Pods
     - Deployment and Jobs
     - Services
     - Volumes and VolumeMounts
     - Template (YAML) files
   - Creating a GPU cluster with AKS
     - **P**:: Create your own cluster (**Can we assume everyone has a subscription?**)
     - **/!\\: Depending on audience size, we might need to assign specific regions to different parts of the room to avoid exhausting resources in the DC**
       - 3 GPUs by person would be ideal, 2 could also work.
     - **P**: Creating a storage account to save our models and logs
   - **P**: Installing `kubectl` and demo of the basic commands
     - `kubectl get <>`
     - `kubectl describe node` and show that the GPU is correctly detected
   - **P**: Scheduling a simple CPU-only job (nginx?)
     - Understanding the YAML file
1. GPU and Kubernetes *10 min*
   - **P**: Sceduling a GPU job (CNTK)
     - Resource Limits
     - Understanding how to mount the NVIDIA drivers
1. Introduction to Helm *5 min*
   - What is Helm
   - **P**: Install Helm
1. Introduction to `TfJob` *10 min*
   - What is `TfJob`, and how it can help us running TensorFlow on K8s
   - **P**: Installing `TfJob` on the cluster
   - **P**: Scheduling a simple TF GPU Job with `TfJob` and monitoring it with TensorBoard
1. Distributed TensorFlow on Kubernetes with `TfJob` *5 min*
   - **P**: Running a distributed TF training 
1. Hyper-Parameter sweeping with Helm *10 min*
   - **P**: Running 3 parrallel trainings 
   - **P**: Comparing the runs live in TensorBoard
1. Going Further *10 min before the end*
   - Autoscaling your cluster
   - Pachyderm
   - NFS

# Timeframe

|Part|Title|Time in minutes|
|-|-|-|
|1|Introduction (PowerPoint)|10|
|2|Other MS tools (PowerPoint)|10|
|3|Introduction to Containers and Docker|20|
|4|Introduction to Kubernetes|25|
|5|GPU and Kubernetes|10|
|6|Introduction to Helm|5|
|7|Introduction to `TfJob`|10|
|8|Distributed TensorFlow on Kubernetes with `TfJob`|5|
|9|Hyper-Parameter sweeping with Helm|10|
|10|Going Further|10 before the end|

## Total = 105min / 1H 45min