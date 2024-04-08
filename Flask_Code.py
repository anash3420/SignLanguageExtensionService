from flask import Flask, send_file, request
import requests
from flask_cors import CORS  # Import CORS
from pose_format import Pose
from pose_format.pose_visualizer import PoseVisualizer
import tempfile
import os


app = Flask(__name__)
CORS(app)  # Initialize CORS with the Flask app

CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/convert-to-video', methods=['POST'])
def convert_to_video():
    # Extract query parameters
    text = request.args.get('text', 'default text')
    spoken = request.args.get('spoken', 'en')
    signed = request.args.get('signed', 'ase')

    # External API URL
    api_url = 'https://us-central1-sign-mt.cloudfunctions.net/spoken_text_to_signed_pose'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }

    # Call the external API
    response = requests.get(api_url, headers=headers,params={"text": text, "spoken": spoken, "signed": signed})

   


    if response.status_code == 200:
        # Read the pose data from the response
        print("in here")
        pose_data = response.content

        # Load the pose data using pose_format
        pose = Pose.read(pose_data)

        # Create a temporary file for the output video
        fd, video_path = tempfile.mkstemp(suffix=".mp4")
        os.close(fd)  # Close the file descriptor

        # Initialize PoseVisualizer and generate the video
        v = PoseVisualizer(pose)
        v.save_video(video_path, v.draw())

        # Send the generated video file as a response
        return send_file(video_path, as_attachment=True, mimetype='video/mp4', download_name='output.mp4')

    else:
        return f"Failed to call external API. Status code: {response.status_code}", 500

if __name__ == "__main__":
    app.run(debug=True)
