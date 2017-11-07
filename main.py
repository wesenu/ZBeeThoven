import tensorflow as tf
import numpy as np
from tensorflow.contrib import rnn

# Parameters
learning_rate = 0.001
training_iters = 2000
display_step = 1000
n_input = 8
vocab_size = 6

# number of units in RNN cell
n_hidden = 512

#model input and output
x = tf.placeholder("float", [None, n_input, 1])
y = tf.placeholder("float", [None, vocab_size]) #one-hot vector

# RNN output node weights and biases
weights = {
	'out': tf.Variable(tf.random_normal([n_hidden, vocab_size]))
}
biases = {
	'out': tf.Variable(tf.random_normal([vocab_size]))
}

def RNN(x, weights, biases):

	# reshape to [1, n_input]
	x = tf.reshape(x, [-1, n_input])

	# Generate a n_input-element sequence of inputs
	# (eg. [had] [a] [general] -> [20] [6] [33])
	x = tf.split(x,n_input,1)

	# 2-layer LSTM, each layer has n_hidden units.
	# Average Accuracy= 95.20% at 50k iter
	#rnn_cell = rnn.MultiRNNCell([rnn.BasicLSTMCell(n_hidden),rnn.BasicLSTMCell(n_hidden)])

	# 1-layer LSTM with n_hidden units but with lower accuracy.
	# Average Accuracy= 90.60% 50k iter
	# Uncomment line below to test but comment out the 2-layer rnn.MultiRNNCell above
	rnn_cell = rnn.BasicLSTMCell(n_hidden)

	# generate prediction
	outputs, states = rnn.static_rnn(rnn_cell, x, dtype=tf.float32)

	# there are n_input outputs but
	# we only want the last output
	return tf.matmul(outputs[-1], weights['out']) + biases['out']

pred = RNN(x, weights, biases)
probs = tf.nn.softmax(pred)

# Loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
optimizer = tf.train.RMSPropOptimizer(learning_rate=learning_rate).minimize(cost)

# Model evaluation
correct_pred = tf.equal(tf.argmax(pred,1), tf.argmax(y,1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initializing the variables
init = tf.global_variables_initializer()

train_seq = [3,2,1,2,3,3,3,3,2,2,2,2,3,5,5,5,3,2,1,2,3,3,3,3,2,2,3,2,1,1,1,1]

with tf.Session() as session:
	session.run(init)
	step = 0
	offset = 0
	while step < training_iters:
		if step % 50 == 0:
			print(step)
		offset = offset % len(train_seq)-n_input
		x_in = [train_seq[i] for i in range(offset,offset+n_input)]
		x_in = np.reshape(np.array(x_in), [-1, n_input, 1])
		symbols_out_onehot = np.zeros([vocab_size], dtype=float)
		symbols_out_onehot[train_seq[offset+n_input]] = 1.0
		symbols_out_onehot = np.reshape(symbols_out_onehot,[1,-1])
		_, acc, loss, onehot_pred = session.run([optimizer, accuracy, cost, pred], \
					feed_dict={x: x_in, y: symbols_out_onehot})

		step += 1
		offset += 1
	print("Done Training")

	current = [3,2,1,2,3,3,3,2]
	for i in range(100):
		next_vals = current[-n_input:]
		keys = np.reshape(np.array(next_vals), [-1, n_input, 1])
		onehot_pred = session.run(pred, feed_dict={x: keys})
		onehot_pred_index = int(tf.argmax(onehot_pred, 1).eval())
		current.append(onehot_pred_index)
	print(current)

'''
# Model parameters
W = tf.Variable([.3], dtype=tf.float32)
b = tf.Variable([-.3], dtype=tf.float32)

# Model input and output
x = tf.placeholder(tf.float32)
linear_model = W*x + b
y = tf.placeholder(tf.float32)

# loss
loss = tf.reduce_sum(tf.square(linear_model - y)) # sum of the squares

# optimizer
optimizer = tf.train.GradientDescentOptimizer(0.01)
train = optimizer.minimize(loss)

# training data
x_train = [1, 2, 3, 4]
y_train = [0, 5, 2, 4]

# training loop
init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init) # reset values to wrong

for i in range(1000):
  sess.run(train, {x: x_train, y: y_train})

# evaluate training accuracy
curr_W, curr_b, curr_loss = sess.run([W, b, loss], {x: x_train, y: y_train})
print("W: %s b: %s loss: %s"%(curr_W, curr_b, curr_loss))
'''