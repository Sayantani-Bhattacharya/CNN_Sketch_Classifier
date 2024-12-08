import torch
from torchvision import transforms, datasets
from dataset import CustomImageDataset
from torch.utils.data import DataLoader
from cnn import CNN
import torch.nn as nn
from PIL import Image
from tqdm import tqdm
from datetime import datetime
# from sketch_interface import Interface
from sklearn.metrics import accuracy_score, precision_score

# Interface = Interface()
# Interface.draw()

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {DEVICE} device")

# Loss lists for plotting
train_losses = []
valid_losses = []
test_losses = []

resize_width = 120
resize_height = 120
#Hyperparameters
batch_size = 16
lr = 0.001
epochs = 10

# Loading and pre-processing data
transform = transforms.Compose([
    transforms.Resize((resize_width, resize_height)),
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

dataset = datasets.ImageFolder("data", transform=transform)
train_set, valid_set = torch.utils.data.random_split(dataset, [0.75, 0.25])
test_image = "user_sketch.png"

train_loader = DataLoader(train_set, batch_size, shuffle=True)
valid_loader = DataLoader(valid_set, batch_size, shuffle=True)

model = CNN(resize_width, resize_height).to(DEVICE)
# Tune this for potential better results
loss_func = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lr)

# Training loop
for epoch in range(epochs):
    model.train()  # Set the model to training mode
    running_loss = 0.0

    for images, labels in train_loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)

        # Zero the parameter gradients
        optimizer.zero_grad()

        # Forward pass
        outputs = model(images)
        loss = loss_func(outputs, labels)

        # Backward pass and optimization
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    print(f"Epoch {epoch+1}/{epochs}, Loss: {running_loss / len(train_loader):.4f}")

now = datetime.now()
formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
# Save the trained model
torch.save(model.state_dict(), f'models/{formatted_time}_sketch_cnn.pth')
print("Training complete and model saved.")
      
        
#Validation Set Loop
model.eval()

valid_loss = 0.0
y_preds = []
y_trues = []

with torch.no_grad():
    for image, labels in valid_loader:
        image, y_true = image.to(DEVICE), labels.to(DEVICE)
        
        y_pred = model(image)
        loss = loss_func(y_pred, y_true)
        valid_loss += loss.item()
        
        y_trues.append(y_true)
        y_preds.append(y_pred)
        
accuracy = accuracy_score(y_trues, y_preds)
precision = precision_score(y_trues, y_preds)

print(f"Accuracy of validation set: {accuracy}")
print(f"Precision of validation set: {precision}")               

# # Validation loop
# # Visualisation section

# # Testing loop

# test_transform = transforms.Compose([
#     # Resize to model's input size
#     transforms.Resize((image_width, image_height)),
#     transforms.ToTensor(),  # Convert PIL to tensor
# ])

# # Load the trained model
# model.load_state_dict(torch.load("final_model.pth"))
# model.eval()  # Set the model to evaluation mode
# print("testing loop...")
# # Process the image and make a prediction
# with torch.no_grad():  # Disable gradient computation for inference
#     # Load and preprocess the image
#     image = Image.open(test_image).convert("L")
#     image = test_transform(image)
#     # Add one axis to the batch dimension
#     image = image.unsqueeze(0).to(DEVICE)

#     # Get the model's prediction
#     output = model(image)
#     # Get the class index with the highest score
#     predicted_label = torch.argmax(output, dim=1).item()
#     print(f"Predicted Label for '{test_image}': {predicted_label} : ")

#     for key, value in dataset.label_map.items():
#         if value == predicted_label:
#             key_for_value = key
#             print(f"the image is of : {key}")
#             break
