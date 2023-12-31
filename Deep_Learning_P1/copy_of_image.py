# -*- coding: utf-8 -*-
"""Copy of Image.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19t-G7jKxiUUYO0zgwGaEaUrB8cyw59e0
"""

# #Mount the google drive
# from google.colab import drive
# drive.mount('/content/Drive')

from google.colab import drive
# drive.mount('/content/drive')

from tensorflow.python.client import device_lib
device_lib.list_local_devices()

import pandas as pd

import os

# Create a list of file paths to your images
image_paths = [os.path.join("/content/drive/MyDrive/traindata1000", filename) for filename in os.listdir("/content/drive/MyDrive/traindata1000")]

# Create a DataFrame
df1 = pd.DataFrame({"Image_Path": image_paths})

from PIL import Image

df1.head()

df1['Image'] = df1['Image_Path'].apply(lambda path: Image.open(path))

df1['Image_Path'].head(100)

df=df1.head(10000)

target_size = (200, 200)

from PIL import Image
for index,imagerow in df.iterrows():
     image=imagerow[1]
     resized_image=image.resize(target_size)
     df.at[index, 'Image'] = resized_image

df_grayscale = df.copy()

for index,imagerow in df_grayscale.iterrows():
     image=imagerow[1]
     converted_image=image.convert('L')

print(df_grayscale.columns)
df_grayscale['GrayScale'] = None

for index,imagerow in df_grayscale.iterrows():
     image=imagerow[1]
     converted_image=image.convert('L')
     df_grayscale.at[index, 'GrayScale'] = converted_image

# Assuming you have a DataFrame named 'df' with a 'Loaded_Image' column containing Pillow Image objects
for index, row in df_grayscale.iterrows():
   if index<5:
    image = row['Image']
    display(image)
    converted_image = row['GrayScale']
    display(converted_image)

from sklearn.model_selection import train_test_split

X = df_grayscale['GrayScale']
Y = df_grayscale['Image']
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.01, random_state=42)

import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Input, Concatenate
from tensorflow.keras.models import Model

# Load your grayscale and color images
def load_images(directory):
    images = []
    for filename in os.listdir(directory):
        img = Image.open(os.path.join(directory, filename))
        images.append(np.array(img))
    return np.array(images)

# Replace these paths with your actual grayscale and color image directories
grayscale_dir = '/path/to/your/grayscale/images/'
color_dir = '/path/to/your/color/images/'

X_train_gray = load_images(grayscale_dir)
Y_train_color = load_images(color_dir)

# Preprocess data
X_train_gray = X_train_gray / 255.0
Y_train_color = Y_train_color / 255.0

# Define the U-Net model
def unet_model(input_shape=(200, 200, 1)):
    inputs = Input(input_shape)

    # Encoder
    conv1 = Conv2D(64, 3, activation='relu', padding='same')(inputs)
    conv1 = Conv2D(64, 3, activation='relu', padding='same')(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = Conv2D(128, 3, activation='relu', padding='same')(pool1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    # Middle
    convm = Conv2D(256, 3, activation='relu', padding='same')(pool2)
    convm = Conv2D(256, 3, activation='relu', padding='same')(convm)

    # Decoder
    up1 = Concatenate()([UpSampling2D(size=(2, 2))(convm), conv2])
    conv3 = Conv2D(128, 3, activation='relu', padding='same')(up1)
    conv3 = Conv2D(128, 3, activation='relu', padding='same')(conv3)

    up2 = Concatenate()([UpSampling2D(size=(2, 2))(conv3), conv1])
    conv4 = Conv2D(64, 3, activation='relu', padding='same')(up2)
    conv4 = Conv2D(64, 3, activation='relu', padding='same')(conv4)

    outputs = Conv2D(3, 1, activation='sigmoid')(conv4)  # Output 3 channels for RGB

    model = Model(inputs=inputs, outputs=outputs)
    return model

# Create an instance of the U-Net model
unet_colorization_model = unet_model()

# Compile the model
unet_colorization_model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
history = unet_colorization_model.fit(X_train_gray, Y_train_color, epochs=10, batch_size=32, validation_split=0.1)

# Visualize training history
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Predict colorized images
predicted_color_images = unet_colorization_model.predict(X_train_gray[:5])

# Visualize some results
for i in range(5):
    plt.figure(figsize=(12, 6))

    # Grayscale Input
    plt.subplot(1, 3, 1)
    plt.imshow(X_train_gray[i].reshape(200, 200), cmap='gray')
    plt.title('Grayscale Input')
    plt.axis('off')

    # Predicted Colorized Output
    plt.subplot(1, 3, 2)
    plt.imshow(predicted_color_images[i])
    plt.title('Predicted Colorized Output')
    plt.axis('off')

    # Ground Truth Color Image
    plt.subplot(1, 3, 3)
    plt.imshow(Y_train_color[i])
    plt.title('Ground Truth Color Image')
    plt.axis('off')

    plt.tight_layout()
    plt.show()