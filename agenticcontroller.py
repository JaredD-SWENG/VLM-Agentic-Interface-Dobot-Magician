import streamlit as st
from PIL import Image
import cv2
import subprocess
import os
import json
import numpy as np
from PIL import ImageDraw, ImageColor
import google.generativeai as genai
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("GEMINI_AI_API_KEY")

# Configure Generative AI API
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash-002',
)

# Additional Colors for Bounding Boxes
additional_colors = [colorname for (
    colorname, colorcode) in ImageColor.colormap.items()]

# Utils for Plotting Bounding Boxes


def plot_bounding_boxes(im, noun_phrases_and_positions):
    img = im
    width, height = img.size

    draw = ImageDraw.Draw(img)
    colors = [
        'red', 'green', 'blue', 'yellow', 'orange', 'pink', 'purple', 'brown',
        'gray', 'beige', 'turquoise', 'cyan', 'magenta', 'lime', 'navy',
        'maroon', 'teal', 'olive', 'coral', 'lavender', 'violet', 'gold',
        'silver'
    ] + additional_colors

    for i, (noun_phrase, (y1, x1, y2, x2)) in enumerate(noun_phrases_and_positions):
        color = colors[i % len(colors)]
        abs_x1 = int(x1 / 1000 * width)
        abs_y1 = int(y1 / 1000 * height)
        abs_x2 = int(x2 / 1000 * width)
        abs_y2 = int(y2 / 1000 * height)

        draw.rectangle(((abs_x1, abs_y1), (abs_x2, abs_y2)),
                       outline=color, width=4)
        draw.text((abs_x1 + 8, abs_y1 + 6), noun_phrase, fill=color)

    save_path = os.path.join(os.getcwd(), "image_with_bounding_boxes.png")
    img.save(save_path)
    return save_path

# Parsing Utils


def parse_list_boxes(text):
    result = []
    for line in text.strip().splitlines():
        try:
            numbers = line.split('[')[1].split(']')[0].split(',')
        except:
            numbers = line.split('- ')[1].split(',')
        result.append([int(num.strip()) for num in numbers])
    return result


# Function to capture image using OpenCV
def capture_image():
    st.write("Accessing webcam...")
    cap = cv2.VideoCapture(0)  # Open the webcam (use 0 for default camera)

    if not cap.isOpened():
        st.error("Could not access the webcam.")
        return None

    ret, frame = cap.read()
    if not ret:
        st.error("Failed to capture image.")
        cap.release()
        return None

    # Save the captured image locally
    img_path = "captured_image.png"
    cv2.imwrite(img_path, frame)

    # Release the webcam and return the image path
    cap.release()

    # Convert BGR (OpenCV) to RGB (Pillow compatible)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    return img_path


# Streamlit App
st.title("VLM Agentic Interface for Dobot Magician")

# Input Section
user_command = st.text_input(
    "Enter your command:", "Move the yellow block to the right of the blue block.")
run_button = st.button("Run")

if run_button:
    # Step 1: Capture an image using OpenCV
    st.write("Capturing image...")
    img_path = capture_image()

    if img_path is None:
        st.error("Image capture failed. Please try again.")
    else:
        st.write("Image captured successfully!")

        # Load the captured image using PIL
        im = Image.open(img_path)

        # Step 1: Get bounding boxes for workspace
        st.write("Getting bounding boxes for workspace from image...")
        workspace_bounding_box = model.generate_content([
            im,
            (
                '''Return bounding boxes for just the flat, white, rectangluar paper in picture in the following format as:\n 
                [ymin, xmin, ymax, xmax]
                Don't change the format. Don't say anything else.'''
            ),
        ])

        # Parse bounding box for workspace
        workspace = parse_list_boxes(workspace_bounding_box.text)
        workspace_dict = {f'workspace': x for i, x in enumerate(workspace)}

        # Display raw output of bounding boxes
        st.write("Workspace Bounding Box Agent:")
        st.text(workspace_bounding_box.text)

        # Step 2: Generate bounding boxes using Generative AI model
        st.write("Generating bounding boxes from image...")
        bounding_boxes = model.generate_content([
            im,
            (
                '''Return bounding boxes for all the blocks in the following format as
                 a list. \n [ymin, xmin, ymax, xmax](block_color). Don't change the format and always put - before each item. Don't say anything else.'''
            ),
        ])

        # Display raw output of bounding boxes
        st.write("Bounding Boxes Agent:")
        st.text(bounding_boxes.text)

        # Step 3: Spatial Analysis
        spatial_analysis = model.generate_content([
            im,
            (
                f'''Given the user's command for a robot arm: {user_command}
                  Descibe the spatial relationship between the all the relavant object in the scene captured in the image. 
                  I DO NOT need the location/bounding boxes. 
                  I need just the approximate size (mm), shape(mm), orientation and spatial relationship of each of the relavant objects.
                  Include anything else that would be useful to know if I will be coming up with a plan to perform the user's command.'''
            ),
        ])

        # Display raw output of bounding boxes
        st.write("Spatial Analysis Agent:")
        st.text(spatial_analysis.text)

        # Parse bounding boxes and plot them on the image
        boxes = parse_list_boxes(bounding_boxes.text)
        boxes_dict = {f'block_{i}': x for i, x in enumerate(boxes)}

        combined_dict = boxes_dict | workspace_dict

        processed_image_path = plot_bounding_boxes(
            im, noun_phrases_and_positions=list(combined_dict.items()))

        # Display processed image with bounding boxes
        st.image(processed_image_path, caption="Image with Bounding Boxes")

        # processed_image_path = plot_bounding_boxes(
        #     im, noun_phrases_and_positions=list(boxes_dict.items()))

        # Step 4: Translate the coordinates
        def corners_to_points(corners):
            ymin, xmin, ymax, xmax = corners
            top_left = (xmin, ymin)
            top_right = (xmax, ymin)
            bottom_left = (xmin, ymax)
            bottom_right = (xmax, ymax)
            return [top_left, top_right, bottom_left, bottom_right]

        def points_to_corners(points):
            top_left, top_right, bottom_left, bottom_right = points
            xmin, ymin = top_left
            xmax, ymax = bottom_right
            return [ymin, xmin, ymax, xmax]

        # Define the robot coordinates for the corners of the paper
        robot_corners = np.array(
            [[300, 100], [300, -100], [200, 100], [200, -100]], dtype=np.float32)

        def transform_coordinates_dict(image_dict, items_dict):
            # Extract image corners from the first dictionary
            image_corners = np.array(image_dict['workspace'], dtype=np.float32)
            st.text(image_corners)
            # Compute the homography matrix
            homography_matrix, _ = cv2.findHomography(
                image_corners, robot_corners)

            # Function to transform a single point
            def transform_point(image_coords):
                point = np.array(
                    [image_coords[0], image_coords[1], 1], dtype=np.float32).reshape(3, 1)
                transformed_point = np.dot(homography_matrix, point)
                x_robot = transformed_point[0] / transformed_point[2]
                y_robot = transformed_point[1] / transformed_point[2]
                return (x_robot[0], y_robot[0])

            # Transform all items in the second dictionary
            transformed_items_dict = {}
            for key, points in items_dict.items():
                transformed_points = [
                    transform_point(point) for point in points]
                transformed_items_dict[key] = transformed_points

            return transformed_items_dict

        for label, corners in boxes_dict.items():
            boxes_dict[label] = corners_to_points(corners)

        workspace_dict['workspace'] = corners_to_points(
            workspace_dict['workspace'])

        transformed_boxes = transform_coordinates_dict(
            workspace_dict, boxes_dict)
        st.text(transformed_boxes)

        for label, points in transformed_boxes.items():
            transformed_boxes[label] = points_to_corners(points)
        st.text(transformed_boxes)

        def add_color_to_dict(input_string, converted_dict):
            # Extract color and bounding box information from the input string
            pattern = r'- \[.*?\]\((.*?)\)'
            colors = re.findall(pattern, input_string)

            # Create a new dictionary with colors included
            colored_dict = {}
            for i, color in enumerate(colors):
                block_key = f'block_{i}'
                if block_key in converted_dict:
                    colored_dict[block_key] = {
                        'coordinates': converted_dict[block_key],
                        'color': color
                    }
            return colored_dict

        colored_dict = add_color_to_dict(
            bounding_boxes.text, transformed_boxes)
        st.text(colored_dict)

        # Step 5: Generate steps to perform the action based on user command and scene
        steps = model.generate_content(f'''
        Based on the scene provided below, generate a list of detailed and specific steps to perform this action using a Dobot Magician robot arm: {user_command}.\n
        Here is the location/bounding boxes of the objects (use these actual values to determine locations, etc.; don't use example locations): {colored_dict}\n
        Here is the spatial analysis of the objects: {spatial_analysis.text}
        ''')

        # Display generated steps
        st.write("Logic Steps Agent:")
        st.text(steps.text)

        # Step 5: Generate Python code for robot arm based on steps
        with open("DobotDllType.txt", encoding="utf-8") as file:
            dobot_dll = file.read()
        with open("CMPSC 497 Robotics Lecture #5 Industrial Robots v3.3.txt", encoding="utf-8") as file:
            example_code = file.read()

        code = model.generate_content([f'''
        Here are a list of steps I want to perform on a Dobot Magician robot arm:\n {steps.text}\n\n
        Now write a Python program to excute these steps. Only return Python code, and no other text (use comments for other info).\n
        I've also attached some example code.''', example_code])

        # Display generated Python code
        st.write("Coding Agent:")
        st.code(code.text, language='python')

        # # Define the file path where the Python code will be written
        file_path = os.path.join(
            "demo-magician-python-64-master", "DobotControl.py")

        # Strip markdown formatting from code.text
        cleaned_code = code.text.strip().removeprefix(
            "```python").removesuffix("```").strip()

        # Write the cleaned code to the specified file
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(cleaned_code)
            st.write(f"Python code successfully written to {file_path}")
        except Exception as e:
            st.write(f"An error occurred while writing to the file: {e}")

        # Get the current working directory
        current_dir = os.getcwd()

        # Navigate to the subfolder where the file is located
        subfolder_path = os.path.join(
            current_dir, "demo-magician-python-64-master")

        # Change the current working directory to the subfolder
        os.chdir(subfolder_path)

        # Run the file using the full path
        subprocess.run(["python", "DobotControl.py"])

        # Restore the original working directory
        os.chdir(current_dir)
