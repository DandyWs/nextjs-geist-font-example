from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import threading
import subprocess
import queue
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Queue to hold real-time packet data
packet_queue = queue.Queue()
capture_thread = None
capture_running = False

def run_tshark():
    global capture_running
    capture_running = True
    cmd = ['tshark', '-i', 'eth0', '-l']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        line = process.stdout.readline()
        if line:
            packet_queue.put(line.strip())
        else:
            break
    process.terminate()

def start_capture_thread():
    global capture_thread, capture_running
    if not capture_running:
        capture_thread = threading.Thread(target=run_tshark, daemon=True)
        capture_thread.start()

start_capture_thread()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    # TODO: Analyze file with CNN model (placeholder)
    result = {'message': f'File {filename} uploaded and analyzed (placeholder)'}
    return jsonify(result)

@app.route('/realtime/start', methods=['POST'])
def start_capture():
    return jsonify({'message': 'Capture is always running'})

@app.route('/realtime/stop', methods=['POST'])
def stop_capture():
    return jsonify({'message': 'Stop not supported in live capture mode'})

@app.route('/realtime/data', methods=['GET'])
def get_realtime_data():
    packets = []
    while not packet_queue.empty():
        packets.append(packet_queue.get())
    # TODO: Analyze packets with CNN model (placeholder)
    return jsonify({'packets': packets})

if __name__ == '__main__':
    app.run(debug=True)
