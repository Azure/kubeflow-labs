import click
import tensorflow as tf
import numpy as np
from skimage.data import astronaut
from scipy.misc import imresize, imsave, imread

img = imread('./starry.jpg')
img = imresize(img, (100, 100))
save_dir = 'output'
epochs = 2000


def linear_layer(X, layer_size, layer_name):
    with tf.variable_scope(layer_name):
        W = tf.Variable(tf.random_uniform([X.get_shape().as_list()[1], layer_size], dtype=tf.float32), name='W')
        b = tf.Variable(tf.zeros([layer_size]), name='b')
        return tf.nn.relu(tf.matmul(X, W) + b)

@click.command()
@click.option("--learning-rate", default=0.01) 
@click.option("--hidden-layers", default=7)
@click.option("--logdir")
def main(learning_rate, hidden_layers, logdir='./logs/1'):
    X = tf.placeholder(dtype=tf.float32, shape=(None, 2), name='X') 
    y = tf.placeholder(dtype=tf.float32, shape=(None, 3), name='y')
    current_input = X
    for layer_id in range(hidden_layers):
        h = linear_layer(current_input, 20, 'layer{}'.format(layer_id))
        current_input = h

    y_pred = linear_layer(current_input, 3, 'output')

    #loss will be distance between predicted and true RGB
    loss = tf.reduce_mean(tf.reduce_sum(tf.squared_difference(y, y_pred), 1))
    tf.summary.scalar('loss', loss)

    train_op = tf.train.AdamOptimizer(learning_rate).minimize(loss)
    merged_summary_op = tf.summary.merge_all()  

    res_img = tf.cast(tf.clip_by_value(tf.reshape(y_pred, (1,) + img.shape), 0, 255), tf.uint8)
    img_summary = tf.summary.image('out', res_img, max_outputs=1)
    
    xs, ys = get_data(img)

    with tf.Session() as sess:
        tf.global_variables_initializer().run()  
        train_writer = tf.summary.FileWriter(logdir + '/train', sess.graph)
        test_writer = tf.summary.FileWriter(logdir + '/test')
        batch_size = 50
        for i in range(epochs):
            # Get a random sampling of the dataset
            idxs = np.random.permutation(range(len(xs)))
            # The number of batches we have to iterate over
            n_batches = len(idxs) // batch_size
            # Now iterate over our stochastic minibatches:
            for batch_i in range(n_batches):
                batch_idxs = idxs[batch_i * batch_size: (batch_i + 1) * batch_size]
                sess.run([train_op, loss, merged_summary_op], feed_dict={X: xs[batch_idxs], y: ys[batch_idxs]})
                if batch_i % 100 == 0:
                    c, summary = sess.run([loss, merged_summary_op], feed_dict={X: xs[batch_idxs], y: ys[batch_idxs]})
                    train_writer.add_summary(summary, (i * n_batches * batch_size) + batch_i)
                    print("epoch {}, (l2) loss {}".format(i, c))           

            if i % 10 == 0:
                img_summary_res = sess.run(img_summary, feed_dict={X: xs, y: ys})
                test_writer.add_summary(img_summary_res, i * n_batches * batch_size)

def get_data(img):
    xs = []
    ys = []
    for row_i in range(img.shape[0]):
        for col_i in range(img.shape[1]):
            xs.append([row_i, col_i])
            ys.append(img[row_i, col_i])

    xs = (xs - np.mean(xs)) / np.std(xs)
    return xs, np.array(ys)

if __name__ == "__main__":
    main()