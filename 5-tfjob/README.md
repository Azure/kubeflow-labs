## TODO:

* Create actual docker image with simple training
* update example templates with this image


# `tensorflow/k8s` and `TfJob`

## Prerequisites

[Link to previous necessary module (if any)]

## Summary

In this module you will learn how `tensorflow/k8s` can greatly simplify our lives when running TensorFlow on Kubernetes.

## `tensorflow/k8s`

As we saw earlier, giving a container access to GPU is not exactly a breeze on Kubernetes: We need to manually mount the drivers from the node into the container and update some environment variables.    
If you already tried to run a distributed TensorFlow training, you know that it's not easy either. Getting the `ClusterSpec` right can be painful if you have more than a couple VMs, and it's also quite brittle (we will look more into distributed TensorFlow in module [6 - Distributed TensorFlow](../6-distributed-tensorflow/README.md).
  
`tensorflow/k8s` is a new project in TensorFlow's organization on GitHub that makes all of this much easier.  

### Kubernetes Custom Resource Definition

Kubernetes has a concept of [Custom Resources](https://kubernetes.io/docs/concepts/api-extension/custom-resources/) (often abreviated CRD) that allows us to create custom object that will then be able to use.  
In the case of `tensorflow/k8s`, after installation a new `TfJob` object will be available in our cluster. This object allows us to easily describe a TensorFlow training.

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

No need to mount drivers nor specify any environment variable!  


### Installation

### <SUB-CONTENT-1>

### <SUB-CONTENT-2>

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