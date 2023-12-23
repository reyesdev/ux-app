from flask import Blueprint, render_template, request, flash
from flask_login import login_required
import os
import base64
import requests
from PIL import Image
import config

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/uploader')
@login_required  # Ensures that only logged-in users can access this route
def uploader_route():
	return render_template('upload.html', result_path=None)

@upload_bp.route('/upload', methods=['POST'])
@login_required  # Ensures that only logged-in users can access this route
def upload_route():
    try:
		# Save the uploaded image to the 'uploads' folder
        upload_folder = 'uploads'
        file = request.files['imageUpload']

        if request.method == 'POST':
            if file:
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, file.filename)
                
                #file.save(file_path)
                # Resize the image before saving
                try:
                    resized_image = resize_image(file, max_dimensions=(800, 800))
                    resized_image.save(file_path)
                except Exception as e:
                    flash('Error resizing image: {}'.format(e), 'danger')
                    file.save(file_path)

                # Function to encode the image
                def encode_image(image_path):
                    with open(image_path, "rb") as image_file:
                        return base64.b64encode(image_file.read()).decode('utf-8')

                # Path to your image
                image_path = file_path
                
                # Getting the base64 string
                base64_image = encode_image(image_path)

                headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.api_key}"
                }

                payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {"role": "system", "content": "You are a user experience designer. With a background in user experience, web accessibility, graphic design and front-end development."},
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": "Provide feedback with recommendations for improvement and format the content output as HTML"
                        },
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                        }
                    ]
                    }
                ],
                "max_tokens": 1000
                }

                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

                x = str(response.json())

                #write response to file
                with open(file.filename+".txt","w+") as f:
                    f.writelines(x)
                    f.close
            
            # Return the path to the processed image
            return render_template('upload.html', result_path=file_path, response_post = response.json())

    except Exception as e:
        return str(e)
    
def resize_image(file, max_dimensions):
    image = Image.open(file)

    # Get the current dimensions of the image
    current_dimensions = image.size

    # Check if resizing is necessary
    if current_dimensions[0] > max_dimensions[0] or current_dimensions[1] > max_dimensions[1]:
        image.thumbnail(max_dimensions)
        return image
    else:
        # If the image is already within the allowed dimensions, return the original image
        return image

# Function to initialize auth routes
def init_upload_routes(app):
    app.register_blueprint(upload_bp)