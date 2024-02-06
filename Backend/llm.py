import base64
import os
import re
import json

import cv2 as cv
import google.generativeai as genai
import numpy as np
import pandas as pd
from dotenv import load_dotenv

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

model = genai.GenerativeModel(
    model_name="gemini-pro-vision",
    generation_config=generation_config,
    safety_settings=safety_settings,
)


def get_insights(image):

    print("Image received")

    img = cv.imdecode(np.frombuffer(image, np.uint8), -1)
    row, col, _ = img.shape

    prompt_parts = [
        {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image,
            }
        },
        f"""
    This an image of a shelf in a shelf in a pharmaceutical store.
    Perform object detection the various different products and provide the following information.
    The image of size: w={col} h={row}
    
    N = Name of the product
    I = illumination level  of the product beteween 0 to 1
    V = visibility of the product between 0 to 1
    P = placement in the shelf relative to eye level (above, below, at eye level, etc.)
    C = proportional coverage of the shelf by the product (minimal, moderate, full, etc.)
    B = the bounding box (x1, x2, y1, y2) of the product
    
    Respond in the format for each product as rows of csv: (N, I, V, P, C, X1, X2, Y1, Y2)
    Only provide the data for the detected products and ignore the rest of the shelf.
    Only respond with the products with highest confidence.
    Response:
    """,
    ]

    print("Prompt created")
    response = model.generate_content(prompt_parts, stream=False)
    data = re.sub(r"[()]", "", response.text)
    data = [d.strip() for d in data.split("\n") if d]
    data = [d.split(",") for d in data]
    data = pd.DataFrame(
        data[1:],
        columns=[
            "Name",
            "Illumination",
            "Visibility",
            "Placement",
            "Coverage",
            "X1",
            "X2",
            "Y1",
            "Y2",
        ],
    )
    data = data.astype(
        {
            "Illumination": float,
            "Visibility": float,
            # "Placement": float,
            # "Coverage": float,
            "X1": int,
            "X2": int,
            "Y1": int,
            "Y2": int,
        }
    )

    image_data = data.to_dict(orient="records")

    for image in image_data:
        cropped_img = img[image["Y1"] : image["Y2"], image["X1"] : image["X2"]]
        _, buffer = cv.imencode(".jpg", cropped_img)
        image["image"] = base64.b64encode(buffer).decode("utf-8")

    return image_data
