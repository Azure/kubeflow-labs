# Train TensorFlow Models at Scale with Kubernetes on Azure

<!-- ## [Learning Objectives](./learningObjectives.md)
## [Presentation Content](./presentationContent.md)
## [Room Organization](./roomOrganization.md) -->

## Prerequisites

1. Have a valid Microsoft Azure subscription allowing the creation of an ACS cluster
1. Docker client installed: [Installing Docker](https://www.docker.com/community-edition)
1. Azure-cli  (2.0) installed: [Installing the Azure CLI 2.0 | Microsoft Docs](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
1. Git cli installed: [Installing Git CLI](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
1. Kubectl installed: [Installing Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
1. Helm installed: [Installing Helm CLI](https://github.com/kubernetes/helm/blob/master/docs/install.md)


## Content Sumary

| | Module | Description |
| --- | --- | --- |
|0| **[Introduction](0-intro)** | Introduction to this workshop. Motivations and goals.|
|1| **[Docker](1-docker)** | Docker and containers 101.|
|2| **[Kubernetes](2-kubernetes)** | Kubernetes important concepts overview.|
|3| **[GPUs](3-gpus)** | How to use GPUs with Kubernetes.|
|4| **[Helm](4-helm)** | Introduction to Helm |
|5| **[TfJob](5-tfjob)** | How to use `tensorflow/k8s` and `TfJob` to deploy a simple TensorFlow training.|
|6| **[Distributed Tensorflow](6-distributed-tensorflow)** | Going distributed with `TfJob`|
|7| **[Hyperparameters Sweep with Helm](7-hyperparam-sweep)** | Using Helm to deploy a large number of training testing different hypothesis, monitoring and comparing them. |
|8| **[Jupyter Notebooks](8-jupyter)** | Easily deploy a Jupyter Notebook instance on Kubernetes. |
|9| **[Going Further](9-going-further)** | Autoscaling, Azure Fuse, GlusterFS etc. |
