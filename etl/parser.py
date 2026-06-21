import zipfile
import json
import hashlib


def extract_streaming_history(zip_path):

    with zipfile.ZipFile(zip_path) as zf:
        events = []
        target_files = [
            name for name in zf.namelist()
            if "Streaming_History_Audio" in name and name.endswith(".json")
        ]
        for name in target_files:
            with zf.open(name) as f:
                events.extend(json.load(f))
    
    return events


def compute_file_hash(uploaded_file):
    uploaded_file.seek(0)
    file_hash = hashlib.sha256(uploaded_file.read()).hexdigest()
    uploaded_file.seek(0)
    return file_hash