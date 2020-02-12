"""
Inference on MNIST
==================

The Akida Execution Engine includes a powerful native learning
algorithm. However, it is also possible to train an Akida-compatible
model externally, using specialized deep-learning techniques, and to
then implement that model within the Akida Execution Engine as an
efficient inference-only tool using the `CNN2SNN
toolkit <../../user_guide/cnn2snn.html>`__. In this tutorial, you will
simply load one such pre-trained model, use it to process the MNIST
dataset, and look at how to make sense of the outputs.

The MNIST dataset is a handwritten digits database. It has a training
set of 60,000 samples, and a test set of 10,000 samples. Each sample
comprises a 28x28 pixel image and an associated label.

"""

######################################################################
# 1. Loading the MNIST dataset
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

# Various imports needed for the tutorial
import os
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import warnings
from tensorflow.keras.utils import get_file
from tensorflow.keras.datasets import mnist
from sklearn.metrics import f1_score, accuracy_score

# Filter warnings
warnings.filterwarnings("ignore", module="matplotlib")

# Akida specific imports
from akida import Model

######################################################################

# Retrieve MNIST dataset
(train_set, train_label), (test_set, test_label) = mnist.load_data()

# Add a dimension to images sets as akida expects 4 dimensions inputs
train_set = np.expand_dims(train_set, -1)
test_set = np.expand_dims(test_set, -1)


######################################################################
# 2. Look at some images from the test dataset
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

# Display a few images from the test set
f, axarr = plt.subplots(1, 4)
for i in range (0, 4):
    axarr[i].imshow(test_set[i].reshape((28,28)), cmap=cm.Greys_r)
    axarr[i].set_title('Class %d' % test_label[i])
plt.show()


######################################################################
# 3. Load the pre-trained Akida model
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The pre-trained neural network model is included in the models/cnn2snn
# directory. You only need to pass this .fbz file to the Akida Execution
# Engine in order to instantiate the model.
#

# Load provided model configuration file
model_file = get_file("gxnor_mnist.fbz",
                      "http://data.brainchip.com/models/gxnor/gxnor_mnist.fbz",
                      cache_subdir='models/gxnor')
model_akida = Model(model_file)
model_akida.summary()


######################################################################
# 4. Classify a single image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Now try processing a single image, say, the first image in the dataset
# that we looked at above:
#

# Test a single example
sample_image = 0
image = test_set[sample_image]
outputs = model_akida.evaluate(image.reshape(1,28,28,1))
print('Input Label: %i' % test_label[sample_image])

# sphinx_gallery_thumbnail_number = 2
f, axarr = plt.subplots(1, 2)
axarr[0].imshow(test_set[sample_image].reshape((28,28)), cmap=cm.Greys_r)
axarr[0].set_title('Class %d' % test_label[sample_image])
axarr[1].bar(range(10),outputs.squeeze())
axarr[1].set_xticks(range(10))
plt.show()

print(outputs.squeeze())


######################################################################
# Consider the output from the model, printed above. As is typical in
# backprop trained models, the final layer here comprises a
# 'fully-connected or 'dense' layer, with one neuron per class in the
# data (here, 10). The goal of training is to maximize the response of the
# neuron corresponding to the label of each training sample, while
# minimizing the responses of the other neurons.
#
# In the bar chart above, you can see the outputs from all 10 neurons. It
# is easy to see that neuron 7 responds much more strongly than the
# others. The first sample is indeed a number 7.
#
# Check this for some of the other samples by editing the value of
# sample_image in the script above (anything from 0 to 9999).
#


######################################################################
# 5. Check performance across a number of samples
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# We've included a utility to test performance across a large number of
# samples. You can run this below.
#

# Check performance against num_samples samples
num_samples = 10000

results = model_akida.predict(test_set[:int(num_samples)], 10)
accuracy = accuracy_score(test_label[:num_samples], results[:num_samples])
f1 = f1_score(test_label[:num_samples],
               results[:num_samples],
               average='weighted')

# For non-regression purpose
assert accuracy > 0.99

# Print model statistics
print("Model statistics")
stats = model_akida.get_statistics()
model_akida.predict(test_set[:20], 10)
for _, stat in stats.items():
    print(stat)

# Display results
print("Accuracy: "+"{0:.2f}".format(100*accuracy)+"% / "
       +"F1 score: "+"{0:.2f}".format(f1))


######################################################################
# Depending on the number of samples you run, you should find a
# performance of around 99% (99.35% if you run all 10000 samples).
#
# Note that classification here is done simply by identifying the neuron
# with the highest activation level. Slightly higher performance is
# actually possible for this model implementation (~99.1 %) if a very
# slightly more complex final classification is applied (with a single
# additional integer subtraction per neuron), but for simplicity we leave
# those details aside here. See the cnn2snn training framework for a full
# description.
#
