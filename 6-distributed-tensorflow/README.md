# TODO

* Frame problem: distributed is hard, easier with TfJob
* Describe how  to grab the `ClusterSpec`
* Show TensorFlow graph in tensorboard with the different devices

# Distributed TensorFlow with `TfJob`

## Prerequisites

[5 - TfJob](../5-tfjob/)

## Summary

In this module we will see how `TfJob` can greatly simplify the deployment and monitoring of distributed TensorFlow training.
  
## "Vanilla" Distributed TensorFlow is Hard

First let's see how we would to setup a distributed TensorFlow training without Kubernetes or `TfJob` (fear not, we are not actually going to do that).  
First, you would have to find or setup a bunch of idle VMs, or physical machine. In most companies, this would already be a feat, and likely require the coordination of multiple department (such as IT) to get the VMs up, running and reserved for your experiment. 
Then you would likely have to do some back and forth with the IT department to be able to setup your training: the VMs need to be able to talk to each others and have stable endpoints, work might be needed to access the data, you would need to upload your TF code on every single machine etc.  
If you had GPU in the mix, it would likely get even harder since GPUs aren't usually just waiting there.  

Assuming you get through this, you now need to modify your model for distributed training.  
Among other things, you will need to setup the `ClusterSpec` ([`tf.train.ClusterSpec`](https://www.tensorflow.org/api_docs/python/tf/train/ClusterSpec)):  a TensorFlow class that allows you to describe the architecture of your cluster. 
For example, if you were to setup a distributed training with a mere 2 workers and 2 parameter servers, your cluster spec would look like this (the `clusterSpec` would most likely not be hardcoded, but passed as argument to your training script as we will see below, this is for illustration):

```python
cluster = tf.train.ClusterSpec({"worker": ["<IP_GPU_VM_1>:2222",
                                           "<IP_GPU_VM_2>:2222"],
                                "ps": ["<IP_CPU_VM_1>:2222",
                                       "<IP_CPU_VM_2>:2222"]})
```
Here we assume that you want your workers to run on GPU VMs and your parameter servers to run on CPU VMs.  

We will not go through the rest of the modifications needed (splitting operation across devices, getting the master session etc.), as we will look at them later and this would be pretty much the same thing no matter how you run your distributed training.

Once your model is ready for distributed training, you need to start it.  
To do that, you will need to connect to every single VM, and pass the `ClusterSpec` as well as the assigned job name (ps or worker) and task index. 
So it would look something like this:

```bash
# On ps0:
$ python trainer.py \
     --ps_hosts=<IP_CPU_VM_1>:2222,<IP_CPU_VM_2>:2222 \
     --worker_hosts=<IP_GPU_VM_1>:2222,<IP_GPU_VM_2>:2222 \
     --job_name=ps --task_index=0
# On ps1:
$ python trainer.py \
     --ps_hosts=<IP_CPU_VM_1>:2222,<IP_CPU_VM_2>:2222 \
     --worker_hosts=<IP_GPU_VM_1>:2222,<IP_GPU_VM_2>:2222 \
     --job_name=ps --task_index=1
# On worker0:
$ python trainer.py \
     --ps_hosts=<IP_CPU_VM_1>:2222,<IP_CPU_VM_2>:2222 \
     --worker_hosts=<IP_GPU_VM_1>:2222,<IP_GPU_VM_2>:2222 \
     --job_name=worker --task_index=0
# On worker1:
$ python trainer.py \
     --ps_hosts=<IP_CPU_VM_1>:2222,<IP_CPU_VM_2>:2222 \
     --worker_hosts=<IP_GPU_VM_1>:2222,<IP_GPU_VM_2>:2222 \
     --job_name=worker --task_index=1
```

At this point your training would finally start.  
However, if for some reason an IP changes (a VM restarts for example), you would need to go back on every VM in your cluster, and restart the training with an updated `ClusterSpec`. (If the IT department of your company is feeling extra-generous they might assign a DNS name to every VM which would already make your life much easier).
If you see that your training is not doing well and you need to update the code, you have to redeploy it on every VM and restart the training everywhere.
If for some reason you want to retrain after a while, you would most likely need to go back to step 1: ask for the VMs to be allocated, redeploy, update the `clusterSpec`.

All this hurdles means that in practice very few people actually bother with distributed training as the time gained might not be worth the energy and time necessary to set it up correctly.

## Distributed TensorFlow with Kubernetes and `TfJob`

Thanksfully, with Kubernetes and `TfJob` things are much, much simpler, making distributed training something you might actually be able to benefit from.


#### A Small Disclaimer
The issues we saw in the first part of this module can be categorized in two groups: 
* Issues with getting access to enough resources for the trainings (VMs, GPU etc)
* Issues with setting up the training itself

The first group of issue is still very dependent on the processes in your company/group. If you need to go through a formal request to get access to extra VMs/GPU, it will still be a hassle and there is nothing Kubernetes can do about that.  
However, Kubernetes makes this process much easier:
* On ACS and AKS you can spin up new VMs with a single command: [`az <acs|aks> scale`](https://docs.microsoft.com/en-us/cli/azure/aks?view=azure-cli-latest#az_aks_scale)
* On acs-engine you can setup autoscaling so that anytime you schedule a training on Kubernetes, the autoscaler will make sure your cluster has all the resources it need to run it, and when your training is completed, it will shut down any idle VMs, making this the best solution in term of cost and effort. While autoscaling is outside the scope of this workshop we will give you pointers in module [9 - Going Furter](../9-going-further).

Setting up the training, however, is drastically simplified with Kubernetes and `TfJob`.

### Overview of `TfJob` distributed training 

So how does `TfJob` works for distributed training? 
Let's look again at what the `TfJobSpec`and `TfReplicaSpec` objects looks like:

**`TfJobSpec` Object**  

| Field | Type| Description |
|-------|-----|-------------|
| ReplicaSpecs | `TfReplicaSpec` array | Specification for a set of TensorFlow processes, defined below |


**`TfReplicaSpec` Object**  

Note the last two parameters `IsDefaultPS` and `TfPort` that we didn't talked about before.

| Field | Type| Description |
|-------|-----|-------------|
| TfReplicaType | `string` | What type of replica are we defining? Can be `MASTER`, `WORKER` or `PS`. When not doing distributed TensorFlow, we just use `MASTER` which happens to be the default value. | 
| Replicas | `int` | Number of replicas of `TfReplicaType`. Again this is useful only for distributed TensorFLow. Default value is `1`. |
| Template | [`PodTemplateSpec`](https://kubernetes.io/docs/api-reference/v1.8/#podtemplatespec-v1-core) | Describes the pod that will be created when executing a job. This is the standard Pod description that we have been using everywhere.  |
| **IsDefaultPS** | `boolean` | Wether the parameter server should be using a default image or a custom one (default to `true`) |

In case the distinction between master and workers is not clear, there is a single master per TensorFlow cluster, and it is in fact a worker. The difference is that the master is the worker that is going to handle the `Session`, write logs and save the model.

As you can see, `TfJobSpec` and `TfReplicaSpec` allow us to easily define the achitecture of the TensorFlow cluster we would like to setup.

Once we have defined this architecure in a `TfJob` template and deployed it with `kubectl create`, the operator will do most of the work for us.  
For each master, worker and parameter server in our TensorFlow cluster, the operator will create a service exposing it.  
It will then create an internal representation of the cluster with each node and it's associated internal DNS name.


For example, if you were to create a `TfJob` with 1 `MASTER`, 2 `WORKERS` and 1 `PS`, this representation would look similar to this:
```json
{  
    "master":[  
        "distributed-mnist-master-5oz2-0:2222"
    ],
    "ps":[  
        "distributed-mnist-ps-5oz2-0:2222"
    ],
    "worker":[  
        "distributed-mnist-worker-5oz2-0:2222",
        "distributed-mnist-worker-5oz2-1:2222"
    ]
}
```

Finally, the operator will create all the necessary pods, and in each one, inject an environment variable named `Tf_CONFIG`, containing the cluster specification above, as well as the respective jab name and task id that each one should assume.  

For example, here is the value of the `TF_CONFIG` environment variable that would be sent to worker 1:

```json
{  
   "cluster":{  
      "master":[  
         "distributed-mnist-master-5oz2-0:2222"
      ],
      "ps":[  
         "distributed-mnist-ps-5oz2-0:2222"
      ],
      "worker":[  
         "distributed-mnist-worker-5oz2-0:2222",
         "distributed-mnist-worker-5oz2-1:2222"
      ]
   },
   "task":{  
      "type":"worker",
      "index":1
   },
   "environment":"cloud"
}
```

As you can see, this completly takes away the responsability of building and maintaining the `ClusterSpec` from you.  
All you have to do, is modify your code to read the `TF_CONFIG` and act accordingly.

### Modifying your model to use `TfJob`'s `TF_CONFIG`

Concretly, let's see how you would modify your code:

```python
# Grab the TF_CONFIG environment variable
tf_config_json = os.environ.get("TF_CONFIG", "{}")

# Deserialize to a python object
tf_config = json.loads(tf_config_json)

# Grab the cluster specification from tf_config and create a new tf.train.ClusterSpec instance with it
cluster_spec = tf_config.get("cluster", {})
cluster_spec_object = tf.train.ClusterSpec(cluster_spec)

# Grab the task assigned to this specific process from the config. job_name might be "worker" and task_id might be 1 for example
task = tf_config.get("task", {})
job_name = task["type"]
task_id = task["index"]

# Configure the TensorFlow server
server_def = tf.train.ServerDef(
    cluster=cluster_spec_object.as_cluster_def(),
    protocol="grpc",
    job_name=job_name,
    task_index=task_id)
server = tf.train.Server(server_def)

# checking if this process is the chief (also called master). The master has the responsibility of creating the session, saving the summaries etc.
is_chief = (job_name == 'master')

# If this process has been assigned a parameter server task, we just join the server and wait.
if job_name == 'ps':
    server.join()
```

As for any distributed TensorFlow training, you will then also need to modify your model to split the operations and variables among the workers and parameter servers as well as create on session on the master.

## Exercices

### Exercice 1

[Assignement description & Useful things/links here]

#### Validation

[steps to ensure verify success]

#### Solution

<details>
<summary><strong>Solution (expand to see)</strong></summary>
<p>
    [solution]
</p>
</details>


## Next Step

[Link to next module]
