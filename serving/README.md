# TensorFlow Serving

## Introduction

TensorFlow Serving is a flexible, high-performance serving system for machine learning models, designed for production environments. TensorFlow Serving makes it easy to deploy new algorithms and experiments, while keeping the same server architecture and APIs. TensorFlow Serving provides out-of-the-box integration with TensorFlow models, but can be easily extended to serve other types of models and data.

## Getting started

## Installation

```commandline
ks init my-model-server
cd my-model-server
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/master/kubeflow
ks pkg install kubeflow/tf-serving
ks env add  cloud
ks env set cloud --namespace ${NAMESPACE}

MODEL_COMPONENT=serveInception
MODEL_NAME=inception
#Replace this with the url to your bucket if using your own model
MODEL_PATH=gs://kubeflow-models/inception
MODEL_SERVER_IMAGE=gcr.io/$(gcloud config get-value project)/model-server:1.0
ks generate tf-serving ${MODEL_COMPONENT} --name=${MODEL_NAME}
ks param set --env=cloud ${MODEL_COMPONENT} modelPath $MODEL_PATH
# If you want to use your custom image.
ks param set --env=cloud ${MODEL_COMPONENT} modelServerImage $MODEL_SERVER_IMAGE
# If you want to have the http endpoint.
ks param set --env=cloud ${MODEL_COMPONENT} deployHttpProxy true
```
