import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Lambda
from tensorflow.keras import backend as K
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from sklearn.model_selection import train_test_split

# File paths
train_csv = '/Users/parthranade/Documents/Hackathon/sign_data/train_data.csv'
test_csv = '/Users/parthranade/Documents/Hackathon/sign_data/test_data.csv'
train_base_path = '/Users/parthranade/Documents/Hackathon/sign_data/train'
test_base_path = '/Users/parthranade/Documents/Hackathon/sign_data/test'
img_size = (150, 150)

# Function to preprocess and load image
def preprocess_image(relative_path, base_path):
    full_path = os.path.join(base_path, relative_path)
    img = load_img(full_path, target_size=img_size, color_mode='grayscale')
    img = img_to_array(img) / 255.0
    return img

# Load pairs from a CSV file
def load_image_pairs(csv_path, base_path):
    df = pd.read_csv(csv_path, header=None, names=["img1", "img2", "label"])
    img1_list = np.array([preprocess_image(row["img1"], base_path) for _, row in df.iterrows()])
    img2_list = np.array([preprocess_image(row["img2"], base_path) for _, row in df.iterrows()])
    labels = df["label"].values.astype(np.float32)
    return img1_list, img2_list, labels

# Load train and test data
X1_train, X2_train, y_train = load_image_pairs(train_csv, train_base_path)
X1_test, X2_test, y_test = load_image_pairs(test_csv, test_base_path)

# Split some of train for validation
X1_train, X1_val, X2_train, X2_val, y_train, y_val = train_test_split(
    X1_train, X2_train, y_train, test_size=0.2, random_state=42)

# Build Siamese base model
def build_base_model():
    input = Input(shape=(150, 150, 1))
    x = Conv2D(32, (3,3), activation='relu')(input)
    x = MaxPooling2D()(x)
    x = Conv2D(64, (3,3), activation='relu')(x)
    x = MaxPooling2D()(x)
    x = Conv2D(128, (3,3), activation='relu')(x)
    x = MaxPooling2D()(x)
    x = Flatten()(x)
    x = Dense(128, activation='relu')(x)
    return Model(input, x)

# Siamese network
base_network = build_base_model()
input_a = Input(shape=(150, 150, 1))
input_b = Input(shape=(150, 150, 1))

processed_a = base_network(input_a)
processed_b = base_network(input_b)
distance = Lambda(lambda tensors: K.abs(tensors[0] - tensors[1]))([processed_a, processed_b])
output = Dense(1, activation='sigmoid')(distance)

model = Model([input_a, input_b], output)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
model.fit([X1_train, X2_train], y_train,
          validation_data=([X1_val, X2_val], y_val),
          batch_size=32,
          epochs=20)

# Evaluate on test set
test_loss, test_acc = model.evaluate([X1_test, X2_test], y_test)
print(f"\nTest Accuracy: {test_acc:.4f}")
