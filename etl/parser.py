import zipfile
import json


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
