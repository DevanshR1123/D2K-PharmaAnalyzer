import base64

import cv2 as cv
import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv
from ultralytics import YOLO
import os

load_dotenv()

genai.configure(api_key=os.getenv("GENAI_API_KEY"))

generation_config = {
    "temperature": 0.8,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

gemini = genai.GenerativeModel(
    model_name="gemini-pro-vision",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

model = YOLO("models/best.pt")


def calculate_visibility_percentage(image, bb):
    x, y, w, h = bb
    # Calculate visibility percentage based on the position of the found medicine
    visibility_percentage = 100 - ((y / image.shape[0]) * 100)
    return visibility_percentage


def calculate_placement_analysis_percentage(image, bb):
    x, y, w, h = bb
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


def calculate_incentive(img):

    print("Image received")
    shelf_img = cv.imdecode(np.frombuffer(img, np.uint8), -1)
    # Perform object detection
    results = model(
        shelf_img,
        save=True,
        show_labels=True,
        show_boxes=True,
    )

    box = None
    for result in results:
        box = result.boxes.xywh

    # Get the bounding box of the detected medicine
    x = float(box[0][0])
    y = float(box[0][1])
    w = float(box[0][2])
    h = float(box[0][3])

    bb = (x, y, w, h)

    print("Object detection complete")
    # Example usage
    visibility_percentage = calculate_visibility_percentage(shelf_img, bb)
    placement_analysis_percentage = calculate_placement_analysis_percentage(
        shelf_img, bb
    )
    lighting_conditions = assess_lighting_conditions(shelf_img, (x, y, w, h))

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

    print("Incentive calculated")

    cropped_img = shelf_img[int(y) : int(y + h), int(x) : int(x + w)]
    _, buffer = cv.imencode(".jpg", cropped_img)
    image = base64.b64encode(buffer).decode("utf-8")

    prompt_parts = [
        {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": img,
            }
        },
        {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": cv.imencode(".jpg", cropped_img)[1].tobytes(),
            }
        },
        f"""
    The first image is a shelf in a pharmaceutical store.
    This an image of a product on a shelf in a pharmaceutical store.

    I = {lighting_conditions}
    V = {visibility_percentage}
    P = {placement_analysis_percentage}
    B = {bb}

    Respond with insights on how the product is placed on the shelf, the visibility of the product, and the lighting conditions.
    Provide suggestions on how to improve the visibility and placement of the product on the shelf.
    Response:
    """,
    ]

    print("Prompt created")
    response = gemini.generate_content(prompt_parts, stream=False)

    return {
        "incentive": incentive,
        "image": image,
        "visibility_percentage": visibility_percentage,
        "placement_analysis_percentage": placement_analysis_percentage,
        "lighting_conditions": lighting_conditions,
        "insights": response.text,
    }
