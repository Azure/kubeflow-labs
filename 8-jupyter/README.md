# Jupyter Notebooks on Kubernetes

## Prerequisites  
* [1 - Docker Basics](../1-docker)
* [2 - Kubernetes Basics and cluster created](../2-kubernetes)

## Summary

In this module, you will learn how to:
* Run Jupyter Notebooks locally using Docker
* Run Jupyter Notebooks on Kubernetes
 
## How Jupyter Notebooks work

The [Jupyter Notebook](http://jupyter.org/) is an open source web application that allows users to create and share documents that contain live code, equations, visualizations, and narrative text for rapid prototyping. It is often used for data cleaning and transformation, numerical simulation, statistical modeling, data visualization, machine learning, and more. To better support exploratory iteration and to accelerate computation of Tensorflow jobs, let's look at how we can include data science tools like Jupyter Notebook with Docker and Kubernetes.

## Exercises

### Exercise 1: Run Jupyter Notebooks locally using Docker

In this first exercise, we will run Jupyter Notebooks locally using Docker. We will use the official tensorflow docker image as it comes with Jupyter notebook.

```console
docker run -it -p 8888:8888 tensorflow/tensorflow
```

#### Validation

To verify, browse to the url in the output log. 

For example: `http://localhost:8888/?token=a3ea3cd914c5b68149e2b4a6d0220eca186fec41563c0413`


### Exercise 2: Run Jupyter Notebooks on Kubernetes

In this exercise, we will run Jupyter Notebooks on a Kubernetes cluster. 

As a prerequisite, you should already have a Kubernetes cluster running, you can follow [module 2 - Kubernetes](../2-kubernetes) to create your own cluster. 

Similar to running Jupyter Notebooks locally using Docker, we can again use the official tensorflow docker image as it comes with Jupyter notebook. But here we can run many instances of Jupyter Notebooks in the cluster to handle additional load.

To run Jupyter Notebook using Kubernetes, you need to: 
* Create a Pod using tensorflow image
* Expose port 8888 to run Jupyter notebook 
* [With GPU] Mount nvidia libraries from the host VM to a custom directory in the container
* Create a Service to run Jupyter Notebook

#### Solution for Exercise 2

Create a yaml file like to the one below.

<details>
<summary><strong>Solution for CPU only (expand to see)</strong></summary>
<p>

```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: tensorflow-server
  name: tensorflow-server
spec:
  ports:
  - port: 8888
    targetPort: 8888
  selector:
    app: tensorflow-server
  type: LoadBalancer
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: tensorflow-server
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: tensorflow-server
    spec:
      containers:
      - args:
        image: tensorflow/tensorflow
        name: tensorflow
        ports:
        - containerPort: 8888
```

</p>
</details>

<details>
<summary><strong>Solution with GPU (expand to see)</strong></summary>
<p>

```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: tensorflow-server
  name: tensorflow-server
spec:
  ports:
  - port: 8888
    targetPort: 8888
  selector:
    app: tensorflow-server
  type: LoadBalancer
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: tensorflow-server
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: tensorflow-server
    spec:
      volumes:
      - name: binaries
        hostPath:
          path: /usr/bin/
      - name: libraries
        hostPath:
          path: /usr/lib/x86_64-linux-gnu
      containers:
      - args:
        command: ["/bin/sh", "-c"]
        args: ["export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu_custom:$LD_LIBRARY_PATH;"]
        image: tensorflow/tensorflow:latest-gpu
        name: tensorflow
        ports:
        - containerPort: 8888
        resources:
          limits:
            alpha.kubernetes.io/nvidia-gpu: 1
        volumeMounts:
        - mountPath: /usr/bin/
          name: binaries
        - mountPath: /usr/lib/x86_64-linux-gnu_custom
          name: libraries
```

</p>
</details>

Save the yaml file, then deploy it to your Kubernetes cluster by running:

```console
kubectl create -f <template-path>
```

#### Validation

After the deployment is created, a pod running tensorflow will be created, along with a new service for the Jupyter notebook. The new service will acquire a new external ip to run Jupyter Notebook on port 8888. This may take few minutes to complete. 

To verify, run the following to view the output log to get the URL and the token for the hosted Jupyter notebook:

```console
kubectl log tensorflow-server-xxxxx

# sample output

http://localhost:8888/?token=2e7c875bd4e72137911d33e209c91d01f7a7b44868cf664d

```

Next to get the public ip for the new service created for Jupyter Notebook, run:

```console
kubectl get svc tensorflow-server -o jsonpath={.status.loadBalancer.ingress[0].ip}

xx.xx.xx.xx
```
From a browser, navigate to the Jupyter notebook with the following URL, replace `PUBLICIP` with the output from previous step:

```
http://<PUBLICIP>:8888/?token=2e7c875bd4e72137911d33e209c91d01f7a7b44868cf664d
```

## Next Step
[Module 9: Going Further](../9-going-further/README.md)







