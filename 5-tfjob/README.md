## TODO:

* Create actual docker image with simple training
* update example templates with this image


# `tensorflow/k8s` and `TfJob`

## Prerequisites

* [3 - GPUs](../3-gpus/README.md)  
* [4 - Helm](../4-helm/README.md)

## Summary

In this module you will learn how `tensorflow/k8s` can greatly simplify our lives when running TensorFlow on Kubernetes.

## `tensorflow/k8s`

As we saw earlier, giving a container access to GPU is not exactly a breeze on Kubernetes: We need to manually mount the drivers from the node into the container and update some environment variables.    
If you already tried to run a distributed TensorFlow training, you know that it's not easy either. Getting the `ClusterSpec` right can be painful if you have more than a couple VMs, and it's also quite brittle (we will look more into distributed TensorFlow in module [6 - Distributed TensorFlow](../6-distributed-tensorflow/README.md).
  
`tensorflow/k8s` is a new project in TensorFlow's organization on GitHub that makes all of this much easier.  


### Installing `tensorflow/k8s`

Installing `tensorflow/k8s` with Helm is very easy, just run the following commands:

```console
> CHART=https://storage.googleapis.com/tf-on-k8s-dogfood-releases/latest/tf-job-operator-chart-latest.tgz
> helm install ${CHART} -n tf-job --wait --replace --set cloud=azure
```

If it worked, you should see something like:

```
NAME:   tf-job
LAST DEPLOYED: Mon Nov 20 14:24:16 2017
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/ConfigMap
NAME                    DATA  AGE
tf-job-operator-config  1     7s

==> v1beta1/Deployment
NAME             DESIRED  CURRENT  UP-TO-DATE  AVAILABLE  AGE
tf-job-operator  1        1        1           1          7s

==> v1/Pod(related)
NAME                              READY  STATUS   RESTARTS  AGE
tf-job-operator-3005087210-c3js3  1/1    Running  1         4s
```

This means that 3 resources were created, a `ConfigMap`, a `Deployment`, and a `Pod`.  
We will see in just a moment what each of them do.

### Kubernetes Custom Resource Definition

Kubernetes has a concept of [Custom Resources](https://kubernetes.io/docs/concepts/api-extension/custom-resources/) (often abreviated CRD) that allows us to create custom object that we will then be able to use.  
In the case of `tensorflow/k8s`, after installation a new `TfJob` object will be available in our cluster. This object allows us to easily describe TensorFlow trainings.

As a refresher, here is what a simple TensorFlow training would look like using "vanilla" kubernetes:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: example-job
spec:
  template:
    metadata:
      name: example-job
    spec:
      restartPolicy: OnFailure
      volumes:
      - name: bin
        hostPath: 
          path: /usr/lib/nvidia-384/bin
      - name: lib
        hostPath: 
          path: /usr/lib/nvidia-384
      containers:
      - name: tensorflow
        image: wbuchwalter/<SAMPLE IMAGE>
        resources:
          requests:
            alpha.kubernetes.io/nvidia-gpu: 1 
        volumeMounts:
        - name: bin
          mountPath: /usr/local/nvidia/bin
        - name: lib
          mountPath: /usr/lib/nvidia
        env:
        - name: LD_LIBRARY_PATH
          value: /usr/lib/nvidia:/usr/lib/x86_64-linux-gnu
```
Here is what the same thing looks like using the new `TfJob` resource:

```yaml
apiVersion: tensorflow.org/v1alpha1
kind: TfJob
metadata:
  name: example-tfjob
spec:
  replicaSpecs:
    - template:
        spec:
          containers:
            - image: wbuchwalter/<SAMPLE IMAGE>
              name: tensorflow
              resources:
                limits:
                  alpha.kubernetes.io/nvidia-gpu: 1
          restartPolicy: OnFailure
```

No need to mount drivers nor specify any environment variable anymore.

#### How does this work?

As we saw earlier, when we installed the Helm chart for `tensorflow/k8s`, 3 resources were created in our cluster:
* A `ConfigMap` named `tf-job-operator-config`
* A `Deployment`
* And a `Pod` named `tf-job-operator`

The `tf-job-operator` pod (simply called the operator, or `TfJob` operator), is going to monitor your cluster, and everytime you create a new resource of type `TfJob`, the will know what to do with it.    
Specifically, when you create a new `TfJob`, the operator will create a new Kubernetes `Job` for it, and automatically mount the drivers and update the environment variable if needed (i.e. when you request a GPU).  

You may wonder how the operator knows which directory needs to be mounted in the container for the NVIDIA drivers: that's where the `ConfigMap` comes into play.  

In K8s, a `ConfigMap` is a simple object that contains key-value pairs. This `ConfigMap` can then be linked with a container to inject some configuration.   

When we installed the Helm chart, we specified which cloud provider we are running on by doing `--set cloud=azure`. 
This creates a `ConfigMap` that contains configuration options specific for Azure, including the list of directory to mount, and which environment variable to update.

We can take a look at what is inside our `tf-job-operator-config` by doing:

```console
kubectl describe configmaps tf-job-operator-config
````

The output is:

```
Name:		tf-job-operator-config
Namespace:	default
Labels:		<none>
Annotations:	<none>

Data
====
controller_config_file.yaml:
----
grpcServerFilePath: /opt/mlkube/grpc_tensorflow_server/grpc_tensorflow_server.py
accelerators:
  alpha.kubernetes.io/nvidia-gpu:
    envVars:
      - name: LD_LIBRARY_PATH
        value: /usr/lib/nvidia:/usr/lib/x86_64-linux-gnu
    volumes:
      - name: lib
        mountPath: /usr/lib/nvidia
        hostPath:  /usr/lib/nvidia-384
      - name: bin
        mountPath: /usr/local/nvidia/bin
        hostPath: /usr/lib/nvidia-384/bin
      - name: libcuda
        mountPath: /usr/lib/x86_64-linux-gnu/libcuda.so.1
        hostPath: /usr/lib/x86_64-linux-gnu/libcuda.so.1
```

If you want to know more:
* [tensorflow/k8s](https://github.com/tensorflow/k8s) GitHub repository
* [Introducing Operators](https://coreos.com/blog/introducing-operators.html), a blog post by CoreOS explaining the Operator pattern

### Trying `TfJob`


## Exercices

### Exercice 1

[Assignement & Useful links here]

#### Validation

#### Solution

<details>
<summary><strong>Solution (expand to see)</strong></summary>
<p>
    [solution]
</p>
</details>


## Next Step

[Link to next module]