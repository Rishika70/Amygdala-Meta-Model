import os
import numpy as np
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from flask import Flask

# Initialize the Flask app
app = Flask(__name__)

# Set up file upload settings
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'tiff', 'pdf', 'mri'}

# Create uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

# Upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the file and update the plot dynamically
        return render_template('index.html', filename=filename)
    
    return 'Invalid file format', 400

# Flask/Dash App Initialization
def create_dash_app():
    # Initialize Dash app inside Flask
    dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')
    
    # Data Processing and Visualization
    def process_data(file_path):
        # Simulate EEG/MRI processing (you can replace this with actual processing)
        eeg_data = np.random.rand(3, 200)  # Placeholder EEG data
        trajectory = np.cumsum(eeg_data, axis=1)
        return trajectory

    @dash_app.callback(
        Output('graph-output', 'figure'),
        Input('upload-data', 'contents')
    )
    def update_graph(contents):
        # If a file is uploaded, process the data and update the graph
        if contents:
            trajectory = process_data(contents)
            # Visualize the trajectory
            figure = {
                'data': [
                    go.Scatter3d(
                        x=trajectory[0, :],
                        y=trajectory[1, :],
                        z=trajectory[2, :],
                        mode='lines',
                        line=dict(color='blue', width=2)
                    )
                ],
                'layout': go.Layout(
                    title="Brain Activity Visualization",
                    scene=dict(
                        xaxis=dict(title="Ego"),
                        yaxis=dict(title="Attention"),
                        zaxis=dict(title="Shame")
                    )
                )
            }
            return figure
        return {}

    dash_app.layout = html.Div([
        html.H1("Brain Activity Tracker"),
        dcc.Upload(
            id='upload-data',
            children=html.Button("Upload EEG/MRI Scan"),
            multiple=False
        ),
        dcc.Graph(id='graph-output')
    ])
    return dash_app

# Create Dash app instance
create_dash_app()

if __name__ == '__name__':
    app.run(debug=True)