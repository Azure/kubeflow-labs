# TensorFlow Serving

## Prerequisites

* [1 - Docker Basics](../1-docker)
* [2 - Kubernetes Basics and cluster created](../2-kubernetes)
* [3 - Helm](../3-helm)
* [4 - Kubeflow](../4-kubeflow)

## Summary

In this section you will learn about:

* Setting up a Minio file storage in our Kubernetes cluster
* Serving trained models using TensorFlow Serving

## Context

TensorFlow Serving is a flexible, high-performance serving system for machine learning models, designed for production environments. TensorFlow Serving makes it easy to deploy new algorithms and experiments, while keeping the same server architecture and APIs. TensorFlow Serving provides out-of-the-box integration with TensorFlow models, but can be easily extended to serve other types of models and data.

## Exercises

### Exercise 1: Setting up file storage

First, we'll get started with a file storage backend.

If you already have a model uploaded to storage, you can skip this step.
If not, you can [download Minio client](https://minio.io/downloads.html#download-client-macos) to your operating system of choice to upload trained and exported model.

As we saw in module [3 - Helm](../3-helm), Helm enables us to package an application in a chart and parametrize it's deployment easily. We'll use Helm to create a Minio deployment in our cluster.

```console
ACCESS_KEY=<your access key>
ACCESS_SECRET_KEY=<your access secret key>

helm install --name minio --set accessKey=$ACCESS_KEY,secretKey=$ACCESS_SECRET_KEY,service.type=LoadBalancer stable/minio
```

```console
SERVICE_IP=$(kubectl get svc minio --template="{{range .status.loadBalancer.ingress}}{{.ip}}{{end}}")
S3_ENDPOINT=${SERVICE_IP}:9000
```

Setting up Minio host:

```console
mc config host add minio $S3_ENDPOINT $ACCESS_KEY $ACCESS_SECRET_KEY
```

Creating a bucket and uploading our trained model:

```console
BUCKET_NAME=kubeflow

mc mb minio/$BUCKET_NAME

mc cp --recursive /path/to/your/exported/model minio/$BUCKET_NAME
```

After this command, you should see files are being uploaded.

### Exercise 2: Setting up TensorFlow Serving model server

In this exercise, we are going to set up a TensorFlow model server and start serving our trained model.

Creating our namespace for serving:

```console
export NAMESPACE=serving

kubectl create namespace $NAMESPACE
```

Creating secret for the Minio storage so TensorFlow Serving container can access it:

```console
kubectl create secret generic serving-creds --from-literal=accessKeyID=${ACCESS_KEY} \
 --from-literal=secretAccessKey=${ACCESS_SECRET_KEY} -n $NAMESPACE
```

Defining variables such as model name, TensorFlow Serving image.

```console
S3_USE_HTTPS=0
S3_VERIFY_SSL=0
JOB_NAME=myjob
MODEL_COMPONENT=mnist
MODEL_NAME=mnist
MODEL_PATH=s3://${BUCKET_NAME}/models/${JOB_NAME}/export/${MODEL_NAME}/
MODEL_SERVER_IMAGE=sozercan/tensorflow-model-server
```

Initalize Kubeflow:

```console
ks init my-model-server
cd my-model-server
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/master/kubeflow
ks pkg install kubeflow/tf-serving@74629b7
```

Setting up environment for Kubeflow:

```console
ks env add azure
ks env set azure --namespace ${NAMESPACE}
```

Generating the template:

```console
ks generate tf-serving ${MODEL_COMPONENT} --name=${MODEL_NAME}
```

Overriding parameters with our own values:

```console
ks param set --env azure ${MODEL_COMPONENT} modelServerImage $MODEL_SERVER_IMAGE
ks param set --env azure ${MODEL_COMPONENT} modelPath $MODEL_PATH
ks param set --env azure ${MODEL_COMPONENT} s3Enable true
ks param set --env azure ${MODEL_COMPONENT} s3SecretName serving-creds
ks param set --env azure ${MODEL_COMPONENT} s3SecretAccesskeyidKeyName accessKeyID
ks param set --env azure ${MODEL_COMPONENT} s3SecretSecretaccesskeyKeyName secretAccessKey
ks param set --env azure ${MODEL_COMPONENT} s3Endpoint $S3_ENDPOINT
ks param set --env azure ${MODEL_COMPONENT} s3AwsRegion us-east-1
ks param set --env azure ${MODEL_COMPONENT} s3UseHttps $S3_USE_HTTPS --as-string
ks param set --env azure ${MODEL_COMPONENT} s3VerifySsl $S3_VERIFY_SSL --as-string
ks param set --env azure ${MODEL_COMPONENT} serviceType LoadBalancer
```

Deploying TensorFlow Serving to our cluster:

```console
ks apply azure -c ${MODEL_COMPONENT}
```

After deploying, you should see a deployment and service in your cluster. You can verify with the following:

```console
kubectl get pods -n ${NAMESPACE}

kubectl get svc -n ${NAMESPACE}
```

### Exercise 3: Using a client to query TensorFlow Serving Model Server

In this exercise, we'll use a client to query the TensorFlow Serving model server.

```
cd 9-serving
```

If you don't have virtualenv installed, you can install with:

```console
pip install virtualenv
```

Setting up our virtual environment:

```console
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Starting our query from the client:

```console
export TF_MODEL_SERVER_HOST=$(kubectl get svc ${MODEL_NAME} -n ${NAMESPACE} --template="{{range .status.loadBalancer.ingress}}{{.ip}}{{end}}")

export TF_MNIST_IMAGE_PATH=data/7.png

python mnist_client.py
```

If everything is working correctly, you should see the output from the model and the inference.

Sample output:

```
outputs {
  key: "classes"
  value {
    dtype: DT_UINT8
    tensor_shape {
      dim {
        size: 1
      }
    }
    int_val: 7
  }
}
outputs {
  key: "predictions"
  value {
    dtype: DT_FLOAT
    tensor_shape {
      dim {
        size: 1
      }
      dim {
        size: 10
      }
    }
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 1.0
    float_val: 0.0
    float_val: 0.0
  }
}


............................
............................
............................
............................
............................
............................
............................
..............@@@@@@........
..........@@@@@@@@@@........
........@@@@@@@@@@@@........
........@@@@@@@@.@@@........
........@@@@....@@@@........
................@@@@........
...............@@@@.........
...............@@@@.........
...............@@@..........
..............@@@@..........
..............@@@...........
.............@@@@...........
.............@@@............
............@@@@............
............@@@.............
............@@@.............
...........@@@..............
..........@@@@..............
..........@@@@..............
..........@@................
............................
Your model says the above number is... 7!
```

## Next Step

[10 - Going Further](../10-going-further)
