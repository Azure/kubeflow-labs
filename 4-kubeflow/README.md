# Kubeflow - Overview and Installation

## Prerequisites

- [1 - Docker](../1-docker/README.md)
- [2 - Kubernetes](../2-kubernetes/README.md)

## Summary

In this module we are going to get an overview of the different components that make up [Kubeflow](https://github.com/kubeflow/kubeflow), and how to install them into our newly deployed Kubernetes cluster.

### Kubeflow Overview

From [Kubeflow](https://github.com/kubeflow/kubeflow)'s own documetation:

> The Kubeflow project is dedicated to making deployments of machine learning (ML) workflows on Kubernetes simple, portable and scalable. Our goal is not to recreate other services, but to provide a straightforward way to deploy best-of-breed open-source systems for ML to diverse infrastructures. Anywhere you are running Kubernetes, you should be able to run Kubeflow.

Kubeflow is composed of multiple components:

- [JupyterHub](https://jupyterhub.readthedocs.io/en/latest/), which allows user to request an instance of a Jupyter Notebook server dedicated to them.
- One or multiple training controllers. These are component that simplifies and manages the deployment of training jobs. For the purpose of this lab we are only going to deploy a training controller for TensorFlow jobs. However the Kubeflow community has started working on controllers for PyTorch and Caffe2 as well.
- A serving component that will help you serve predictions with your models.

For more general info on Kubeflow, head to the repo's [README](https://github.com/kubeflow/kubeflow/blob/master/README.md).

### Deploying Kubeflow

Kubeflow uses [`ksonnet`](https://github.com/ksonnet/ksonnet) templates as a way to package and deploy the different components.

> ksonnet simplifies defining an application configuration, updating the configuration over time, and specializing it for different clusters and environments.

First, install ksonnet version [0.13.1](https://ksonnet.io/#get-started), or you can [download a prebuilt binary](https://github.com/ksonnet/ksonnet/releases/tag/v0.13.1) for your OS.

Then run the following commands to download Kubeflow:

```bash
KUBEFLOW_SRC=kubeflow

mkdir ${KUBEFLOW_SRC}
cd ${KUBEFLOW_SRC}

export KUBEFLOW_TAG=v0.4.1

curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
```

`KUBEFLOW_SRC` a directory where you want to download the source to

`KUBEFLOW_TAG` a tag corresponding to the version to check out, such as master for the latest code.

```bash
# Initialize a kubeflow app
KFAPP=mykubeflowapp
${KUBEFLOW_SOURCE}/scripts/kfctl.sh init ${KFAPP} --platform none

# Generate kubeflow app
cd ${KFAPP}
${KUBEFLOW_SOURCE}/scripts/kfctl.sh generate k8s

# Deploy Kubeflow app
${KUBEFLOW_SOURCE}/scripts/kfctl.sh apply k8s
```

### Validation

`kubectl get pods -n kubeflow`

should return something like this:

```
NAME                                READY     STATUS    RESTARTS   AGE
kubeflow      ambassador-b4d9cdb8-2qgww                                 1/1     Running     0          111m
kubeflow      ambassador-b4d9cdb8-hpwdc                                 1/1     Running     0          111m
kubeflow      ambassador-b4d9cdb8-khg8l                                 1/1     Running     0          111m
kubeflow      argo-ui-6d6658d8f7-t6whw                                  1/1     Running     0          110m
kubeflow      centraldashboard-6f686c5b7c-462cq                         1/1     Running     0          111m
kubeflow      jupyter-0                                                 1/1     Running     0          111m
kubeflow      katib-ui-6c59754c48-mgf62                                 1/1     Running     0          110m
kubeflow      metacontroller-0                                          1/1     Running     0          111m
kubeflow      minio-d79b65988-6qkxp                                     1/1     Running     0          110m
kubeflow      ml-pipeline-66df9d86f6-rp245                              1/1     Running     0          110m
kubeflow      ml-pipeline-persistenceagent-7b86dbf4b5-rgndj             1/1     Running     0          110m
kubeflow      ml-pipeline-scheduledworkflow-84f6477479-9tvhk            1/1     Running     0          110m
kubeflow      ml-pipeline-ui-f76bb5f97-2s5qb                            1/1     Running     0          110m
kubeflow      mysql-ffc889689-xkpxb                                     1/1     Running     0          110m
kubeflow      pytorch-operator-ff46f9b7d-qkbvh                          1/1     Running     0          111m
kubeflow      spartakus-volunteer-5b6c956c8f-2gnvb                      1/1     Running     0          111m
kubeflow      studyjob-controller-b7cdbd4cd-nf9z5                       1/1     Running     0          110m
kubeflow      tf-job-dashboard-7746db84cf-njdzk                         1/1     Running     0          111m
kubeflow      tf-job-operator-v1beta1-5949f668f7-j5zrn                  1/1     Running     0          111m
kubeflow      vizier-core-7c56465f6-t6d5p                               1/1     Running     0          110m
kubeflow      vizier-core-rest-67f588b4cb-lqvgr                         1/1     Running     0          110m
kubeflow      vizier-db-86dc7d89c5-8vtfs                                1/1     Running     0          110m
kubeflow      vizier-suggestion-bayesianoptimization-7cb546fb84-tsrn4   1/1     Running     0          110m
kubeflow      vizier-suggestion-grid-6587f9d6b-92c9h                    1/1     Running     0          110m
kubeflow      vizier-suggestion-hyperband-8bb44f8c8-gs72m               1/1     Running     0          110m
kubeflow      vizier-suggestion-random-7ff5db687b-bjdh5                 1/1     Running     0          110m
kubeflow      workflow-controller-cf79dfbff-lv7jk                       1/1     Running     0          110m
```

The most important components for the purpose of this lab are `jupyter-0` which is the JupyterHub spawner running on your cluster, and `tf-job-operator-v1beta1-5949f668f7-j5zrn` which is a controller that will monitor your cluster for new TensorFlow training jobs (called `TfJobs`) specifications and manages the training, we will look at this two components later.

### Remove Kubeflow

If you want to remove the Kubeflow deployment, you can run the following to remove the namespace and installed components:

```bash
cd ${KUBEFLOW_SRC}/${KFAPP}
${KUBEFLOW_SRC}/scripts/kfctl.sh delete k8s
```

## Next Step

[5 - JupyterHub](../5-jupyterhub/README.md)
