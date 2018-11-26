import tensorflow as tf
import random
import aubio

noteDict = {
        "A": 1,
        "A#": 2,
        "B": 3,
        "C": 4,
        "C#": 5,
        "D": 6,
        "D#": 7,
        "E": 8,
        "F": 9,
        "F#": 10,
        "G": 11,
        "G#": 12
    }

#this net will have one input and 12 outputs

def make_frequency_to_note_neural_net():
    # all variables are prefixed with f2n so that the tensorflow session can
    # differentiate between the variables relevant to this neural net and the
    # chord neural net.

    # setting up inputs and outputs
    f2n_inputs = tf.placeholder(tf.float32, [None, 1])
    f2n_outputs = tf.placeholder(tf.float32, [None, 12])

    # setting up weights and biases for inputs->hiddens
    f2n_weights_in = tf.Variable(tf.random_normal([1, 15], stddev=0.03), name='f2n_weights_in')
    f2n_biases_in = tf.Variable(tf.random_normal([15]), name='f2n_biases_in')

    # setting up weights and biases for hiddens->outputs
    f2n_weights_out = tf.Variable(tf.random_normal([15, 12], stddev=0.03), name='f2n_weights_out')
    f2n_biases_out = tf.Variable(tf.random_normal([12]), name='f2n_biases_out')

    # setting up math for hidden layer output
    f2n_hidden_out = tf.add(tf.matmul(f2n_inputs, f2n_weights_in), f2n_biases_in)
    f2n_hidden_out = tf.nn.relu(f2n_hidden_out)

    # setting up math for outputs
    f2n_output_values = tf.nn.softmax(tf.add(tf.matmul(f2n_hidden_out, f2n_weights_out), f2n_biases_out))

    # setting up math for backpropagation
    f2n_outputs_clipped = tf.clip_by_value(f2n_output_values, 1e-10, 0.9999999)
    f2n_cross_entropy = -tf.reduce_mean(tf.reduce_sum(f2n_outputs * tf.log(f2n_outputs_clipped) + (1 - f2n_outputs) * tf.log(1 - f2n_outputs_clipped), axis=1))

    #set up optimizer
    f2n_optimizer = tf.train.GradientDescentOptimizer(0.05)
    f2n_train_step = f2n_optimizer.minimize(f2n_cross_entropy)

    # set up initialisation operator
    f2n_init = tf.global_variables_initializer()

    # function for correct prediction
    f2n_correct_prediction = tf.equal(tf.argmax(f2n_outputs, 1), tf.argmax(f2n_output_values, 1))
    
    # function for accuracy
    f2n_accuracy = tf.reduce_mean(tf.cast(f2n_correct_prediction, tf.float32))
    
    #create session
    f2n_sess = tf.Session()

    #initialize session variables
    f2n_sess.run(f2n_init)

    batch_size = 100
    
    for epoch in range(0, 1000000):
        #train first net
        f2n_freq = [0]*batch_size
        correct_out = [None]*batch_size
        for i in range(batch_size):
            correct_out[i] = [0]*12
            f2n_freq[i] = [random.randrange(0, 23000)]

            #find desired note, continue if frequency is invalid
            try:
                f2n_desired = aubio.freq2note(f2n_freq[i])[:-1]
            except:
                continue


            try:
                correct_out[i][noteDict[f2n_desired]-1] = 1
            except:
                continue

        a, c, _ = f2n_sess.run([f2n_accuracy, f2n_cross_entropy, f2n_train_step], feed_dict={f2n_inputs: f2n_freq, f2n_outputs: correct_out})

        if (epoch + 1) % 1000 == 0: 
            print("Train Data Loss: " + str(c))
            print("Train Data Accuracy: " + str(100.00*a) + "%")
            print()

    return f2n_sess
