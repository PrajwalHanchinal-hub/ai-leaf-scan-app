import os
import json
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint

# -----------------------
# Dataset Paths
# -----------------------
TRAIN_DIR = r"E:\archive\PlantVillage\train"
VAL_DIR = r"E:\archive\PlantVillage\val"

IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 10

# -----------------------
# Data Generators
# -----------------------
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

val_generator = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

# -----------------------
# Save Labels
# -----------------------
labels = list(train_generator.class_indices.keys())

os.makedirs("model", exist_ok=True)

with open("model/labels.json", "w") as f:
    json.dump(labels, f, indent=4)

print("Labels saved.")

# -----------------------
# MobileNetV2
# -----------------------
base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(224,224,3)
)

base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.3)(x)
outputs = Dense(len(labels), activation="softmax")(x)

model = Model(inputs=base_model.input, outputs=outputs)

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

checkpoint = ModelCheckpoint(
    "model/model.h5",
    monitor="val_accuracy",
    save_best_only=True
)

history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    callbacks=[checkpoint]
)

print("Training Completed!")
print("Model saved in model/model.h5")