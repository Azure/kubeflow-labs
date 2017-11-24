* http://cs.stanford.edu/people/karpathy/convnetjs/demo/image_regression.html

# Hyper Parameters Sweep with `TfJob` and Helm

## Prerequisites

[4 - Helm](../4-Helm)
[5 - TfJob](../5-tfjob)

### "Vanilla" Hyperparameter Sweep

Just as distributed training, automated hyperparameter sweeping is also very rarely used in many organizations.  
The reasons are similar. It takes a lot of resources, or time, to run more than a couple training for the same model.
  * Either you run different hypothesis in parallel, which will likely requires a lot of resources and VMs. These VMs need to be managed by someone, the model need to be deployed, logs and checkpoints have to be gathered etc.
  * Or you run everything sequentially on a few number of VMs, which takes a lot of time before being able to compare result

So in practice most people just run a few trainings based on their intuition of what the optimal hyperparameters should be and pick a winner.  

### Kubernetes + Helm

Kubernetes coupled with Helm can make this easier as we will see. 
Because Kubernetes on Azure also allows you to scale very easily (manually or automatically), this allows you to explore a very large hyperparameter space, while maximizing the usage of your cluster (and thus optimizing cost).

In practice, this process is still rudimentary today as the technologies involved are all pretty young. Most likely tools better suited for doing hyperparameter sweeping in distributed systems will soon be available, but in the meantime Kubernetes and Helm already allow us to deploy a large number of trainings fairly easily.

### Why Helm?

As we saw in module [4 - Helm](../4-helm), Helm enables us to package an application in a chart and parametrize it's deployment easily.  
To do that, Helm allows us to use Golang templating engine in the chart definitions. This means we can use conditions, loops, variables and [much more](https://docs.helm.sh/chart_template_guide).  
This will allow us to create complex deployment flow.   

In the case of hyperparameters sweeping, we will want to deploy a number of `TfJobs` each trying different values for some hyperparameters.  
We will also want to deploy a single TensorBoard instance monitoring all these `TfJobs`, that way we can quickly compare all our hypothesis, and even early-stop jobs that clearly don't perform well if we want to reduce cost as much as possible.

## Exercise

### Creating and Deploying the Chart
In this excercise, you will create a new Helm chart that will deploy a number of `TfJobs` as well as a TensorBoard instance.

Here is what our `values.yaml` file could look like for example (you are free to go a different route):

```yaml
image: <IMAGE>
training:
  LearningRateSweep:
    - 0.0001
    - 0.001
  hiddenLayersSweep:
    - 4
    - 5
```

That way, when installing the chart, 4 `TfJob` will actually get deployed:
* 4 hidden layers and learning rate of 0.0001
* 4 hidden layers and learning rate of 0.001
* 5 hidden layers and learning rate of 0.0001
* 5 hidden layers and learning rate of 0.001

This is a very simple example (our model is also very simple), but hopefully you start to see the possibilities than Helm opens.

In this excercise, we are going to use a new model based on [Andrej Karpathy's Image painting demo](http://cs.stanford.edu/people/karpathy/convnetjs/demo/image_regression.html).  
This model objective is to to create a new picture as close as possible to the original one:

![Starry](./src/starry.jpg)

The source code is located in [src/](./src/).  

Our model takes 3 parameters that we can tweak:

| argument | description | default value |
|------|-------------|---------------|
|`--learning-rate` | Learning rate value | `0.001` | 
|`--hidden-layers` | Number of hidden layers in our network. | `4` | 
|`--log-dir` | Path to save TensorFlow's summaries | `None`| 

For simplicity, docker images have already been created so you don't have to build and push yourself:
* `wbuchwalter/helm-tf-hyperparam-sweep:cpu` for CPU only.
* `wbuchwalter/helm-tf-hyperparam-sweep:gpu` for GPU.  

The goal of this exercise is to create an Helm chart that will allow us to test as many variations and combinations of the two hyperparameters `--learning-rate`and `--hidden-layers` as we want by just adding them in our `values.yaml` file.   
This chart should also deploy a single TensorBoard instance (and it's associated service), so we can quickly monitor and compare our different hypothesis.

If you are pretty new to Kubernetes and Helm and don't feel like building your own helm chart just yet, you can skip to the solution where details and explanations are provided.

#### Validation



<details>
<summary><strong>Solution (expand to see)</strong></summary>
<p>
    
</p>
</details>


## Next Step

[Link to next module]
