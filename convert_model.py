import tensorflow as tf
from tensorflow.keras.models import load_model

model = load_model(
    "model/model.h5",
    compile=False
)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open("model/model.tflite", "wb") as file:
    file.write(tflite_model)

print("model.tflite created successfully")