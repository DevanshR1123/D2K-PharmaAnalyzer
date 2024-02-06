import numpy as np
from ultralytics import YOLO
import cv2 as cv

# Load a model
model = YOLO("./best.pt")

# Run batched inference on a list of images
results = model.predict(
    [
        cv.imread(
            "datasets/train/images/WhatsApp-Image-2024-02-05-at-8-45-47-PM_jpeg.rf.65894a3767b8950803aa680cc5b0afab.jpg"
        )
    ],
    save=True,
    show_labels=True,
    show_boxes=True,
)  # return a list of Results objects

box = None
for result in results:
    box = result.boxes.xywh

x = float(box[0][0])
y = float(box[0][1])
w = float(box[0][2])
h = float(box[0][3])


def calculate_visibility_percentage(image, target_medicine):
    # Calculate visibility percentage based on the position of the found medicine
    visibility_percentage = 100 - ((y / image.shape[0]) * 100)
    return visibility_percentage


def calculate_placement_analysis_percentage(image, target_medicine):

    # Calculate placement analysis percentage based on the position of the found medicine
    placement_analysis_percentage = 100 - ((x / image.shape[1]) * 100)
    return placement_analysis_percentage


def assess_lighting_conditions(image, target_region):
    # Crop the image to focus on the region where the medicine is placed
    x, y, w, h = target_region
    target_region_img = image[int(y) : int(y + h), int(x) : int(x + w)]

    # Convert the cropped region to grayscale
    gray = cv.cvtColor(target_region_img, cv.COLOR_BGR2GRAY)

    # Calculate the average pixel intensity to assess lighting conditions
    average_intensity = np.mean(gray)

    if average_intensity > 200:
        light = "Very well lit"
        light_percentage = 80
    elif 150 < average_intensity <= 200:
        light = "Medium lighting"
        light_percentage = 60
    else:
        light = "Low lighting"
        light_percentage = 35

    return light_percentage


# Load the image and target medicine template
image = cv.imread(
    "datasets/valid/images/WhatsApp-Image-2024-02-05-at-8-45-47-PM_jpeg.rf.65894a3767b8950803aa680cc5b0afab.jpg"
)
target_medicine_template = cv.imread(
    "datasets/valid/images/WhatsApp-Image-2024-02-05-at-8-45-47-PM_jpeg.rf.65894a3767b8950803aa680cc5b0afab.jpg",
    cv.IMREAD_GRAYSCALE,
)

# Example usage
visibility_percentage = calculate_visibility_percentage(image, target_medicine_template)
placement_analysis_percentage = calculate_placement_analysis_percentage(
    image, target_medicine_template
)
lighting_conditions = assess_lighting_conditions(
    image, (x, y, w, h)
)  # Replace (x, y, w, h) with the actual coordinates of the detected medicine

# print(f"Visibility Percentage: {visibility_percentage}%")
# print(f"Placement Analysis Percentage: {placement_analysis_percentage}%")
# print(f"Lighting Conditions: {lighting_conditions}")

incentive_percent = (
    (visibility_percentage + placement_analysis_percentage + lighting_conditions)
    * 10000
) / 280

incentive = None

if 300 >= incentive_percent >= 230:
    incentive = 10000
elif incentive_percent > 150:
    incentive = 7142
elif incentive_percent > 100:
    incentive = 5357
else:
    incentive = 3571

print(x, y, w, h, incentive)
