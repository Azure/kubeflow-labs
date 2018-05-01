# Kubeflow - Overview and Installation

## Prerequisites

* [1 - Docker](../1-docker/README.md)
* [2 - Kubernetes](../2-kubernetes/README.md)

## Summary

In this module we are going to get an overview of the different components that make up [Kubeflow](https://github.com/kubeflow/kubeflow), and how to install them into our newly deployed Kubernetes cluster.

### Kubeflow Overview

From [Kubeflow](https://github.com/kubeflow/kubeflow)'s own documetation:

> The Kubeflow project is dedicated to making deployments of machine learning (ML) workflows on Kubernetes simple, portable and scalable. Our goal is not to recreate other services, but to provide a straightforward way to deploy best-of-breed open-source systems for ML to diverse infrastructures. Anywhere you are running Kubernetes, you should be able to run Kubeflow.

Kubeflow is composed of multiple components:
* [JupyterHub](https://jupyterhub.readthedocs.io/en/latest/), which allows user to request an instance of a Jupyter Notebook server dedicated to them.
* One or multiple training controllers. These are component that simplifies and manages the deployment of training jobs. For the purpose of this lab we are only going to deploy a training controller for TensorFlow jobs. However the Kubeflow community has started working on controllers for PyTorch and Caffe2 as well.
* A serving component that will help you serve predictions with your models.

For more general info on Kubeflow, head to the repo's [README](https://github.com/kubeflow/kubeflow/blob/master/README.md).

### Deploying Kubeflow

Kubeflow uses [`ksonnet`](https://github.com/ksonnet/ksonnet) templates as a way to package and deploy the different components.  

> ksonnet simplifies defining an application configuration, updating the configuration over time, and specializing it for different clusters and environments. 

First, install ksonnet version [0.9.2](https://ksonnet.io/#get-started).

Then run the following commands to deploy Kubeflow in your Kubernetes cluster:

```bash
# Create a namespace for kubeflow deployment
NAMESPACE=kubeflow
kubectl create namespace ${NAMESPACE}

# Which version of Kubeflow to use
# For a list of releases refer to:
# https://github.com/kubeflow/kubeflow/releases
VERSION=v0.1.2

# Initialize a ksonnet app. Set the namespace for it's default environment.
APP_NAME=my-kubeflow
ks init ${APP_NAME}
cd ${APP_NAME}
ks env set default --namespace ${NAMESPACE}

# Add a reference to Kubeflow's ksonnet manifests
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/${VERSION}/kubeflow

# Install Kubeflow components
ks pkg install kubeflow/core@${VERSION}
ks pkg install kubeflow/tf-serving@${VERSION}
ks pkg install kubeflow/tf-job@${VERSION}

# Create templates for core components
ks generate kubeflow-core kubeflow-core

# Customize Kubeflow's installation for AKS
ks param set kubeflow-core cloud aks

# Enable collection of anonymous usage metrics
# Skip this step if you don't want to enable collection.
ks param set kubeflow-core reportUsage true
ks param set kubeflow-core usageId $(uuidgen)

# Deploy Kubeflow
ks apply default -c kubeflow-core
```

### Validation

`kubectl get pods -n kubeflow`

should return something like this:

```
NAME                                READY     STATUS    RESTARTS   AGE
ambassador-7789cddc5d-czf7p         2/2       Running   0          1d
ambassador-7789cddc5d-f79zp         2/2       Running   0          1d
ambassador-7789cddc5d-h57ms         2/2       Running   0          1d
centraldashboard-d5bf74c6b-nn925    1/1       Running   0          1d
tf-hub-0                            1/1       Running   0          1d
tf-job-dashboard-8699ccb5ff-9phmv   1/1       Running   0          1d
tf-job-operator-646bdbcb7-bc479     1/1       Running   0          1d
```

The most important components for the puporse of this lab are `tf-hub-0` which is the JupyterHub spawner running on your cluster, and `tf-job-operator-646bdbcb7-bc479` which is a controller that will monitor your cluster for new TensorFlow training jobs (called `TfJobs`) specifications and manages the training, we will look at this two components later.

## Next Step

[5 - JupyterHub](../5-jupyterhub)
