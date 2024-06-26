from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import ml

from concurrent.futures import ThreadPoolExecutor
threadpool = ThreadPoolExecutor(max_workers=5)

# Create a Flask web application
app = Flask(__name__)

# Configure CORS with a list of allowed origins
cors = CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://log-analysis.com:3000"]}})

# Define the directory where you want to save the uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

predictionResults = {}

def runPrediction(filePath):
    predictionResults[filePath] = ml.getPrediction(filePath)
 
# Define a route for the home page
@app.route('/')
def hello_world():
    return 'Working!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    # You can process the uploaded file here.
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if ".csv" not in file.filename:
        return jsonify({"success": False})

    # Ensure the 'uploads' directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Save the uploaded file to the 'uploads' directory
    filePath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filePath)
    # For example, you can save it to a specific directory.
        
    threadpool.submit(runPrediction, filePath)

    # For demonstration, let's just return a success message.
    return jsonify({'message': 'File successfully uploaded',"success":True,"filename":file.filename})

@app.route('/head_of_file', methods=['get'])
def head_of_file():
    try:
        with open("uploads/"+request.args.get("filename")) as f:
            linesList = list()
            f.readline()
            for x in range(10):
                linesList.append(f.readline())
            
        linesList = list(map(str.strip, linesList))
        
        return jsonify({
            "fileName": request.args.get("filename"),
            "lines": linesList
        })
    except Exception as e:
        return jsonify({"status":"error" + e })
    
# Define a route for the home page
@app.route('/predictions')
def predictions():
    global predictionResults
    return jsonify(predictionResults)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
