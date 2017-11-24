import click
import tensorflow as tf
import numpy as np
from skimage.data import astronaut
from scipy.misc import imresize, imsave, imread

img = imread('./starry.jpg')
img = imresize(img, (100, 100))
save_dir = 'output'
epochs = 200000


def distance(p1, p2):
    return tf.pow((p1 - p2), 2)

def negative_color_distance(p1, p2):
    n = [255, 255, 255]
    target = (p1 - n) * -1
    return tf.abs(target - p2)

def linear_layer(X, layer_size, layer_name):
    with tf.variable_scope(layer_name):
        W = tf.Variable(tf.random_uniform([X.get_shape().as_list()[1], layer_size], dtype=tf.float32), name='W')
        b = tf.Variable(tf.zeros([layer_size]), name='b')
        # tf.summary.scalar('W', W)
        # tf.summary.scalar('b', b)
        return tf.nn.relu(tf.matmul(X, W) + b)

@click.command()
@click.option("--learning-rate", default=0.001) 
@click.option("--hidden-layers", default=4)
@click.option("--log-dir")
def main(learning_rate, hidden_layers, log_dir='./logs/1'):

    X = tf.placeholder(dtype=tf.float32, shape=(None, 2), name='X') 
    y = tf.placeholder(dtype=tf.float32, shape=(None, 3), name='y')
    current_input = X
    for layer_id in range(hidden_layers):
        h = linear_layer(current_input, 64, 'layer{}'.format(layer_id))
        current_input = h
    y_pred = linear_layer(current_input, 3, 'output')

    res_img = tf.cast(tf.clip_by_value(tf.reshape(y_pred, (1,) + img.shape), 0, 255), tf.uint8)
    tf.summary.image('out', res_img, max_outputs=1)

    #loss will be distance between predicted and true RGB
    loss = tf.reduce_sum(distance(y_pred, y))
    tf.summary.scalar('loss', loss)
    train_op = tf.train.AdamOptimizer(learning_rate).minimize(loss)
    merged_summary_op = tf.summary.merge_all()  
    
    xs, ys = get_data(img)

    with tf.Session() as sess:
        tf.global_variables_initializer().run()        
        summary_writer = tf.summary.FileWriter(log_dir, graph=tf.get_default_graph())

        for i in range(epochs):
            _, c, summary = sess.run([train_op, loss, merged_summary_op], feed_dict={X: xs, y: ys})
            
            if i % 100 == 0:
                print(i, c)               
                summary_writer.add_summary(summary, i)

def get_data(img):
    xs = []
    ys = []
    for row_i in range(img.shape[0]):
        for col_i in range(img.shape[1]):
            xs.append([row_i, col_i])
            ys.append(img[row_i, col_i])

    xs = (xs - np.mean(xs)) / np.std(xs)
    return xs, ys

if __name__ == "__main__":
    main()