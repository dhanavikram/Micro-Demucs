from flask import Flask, request, jsonify, send_file
import redis
import jsonpickle
import hashlib
import base64
import os
import io
from minio import Minio
import platform
import sys

REDIS_HOST = os.getenv("REDIS_HOST") or 'localhost'
REDIS_PORT = os.getenv("REDIS_PORT") or 6379
MINIO_HOST = os.getenv("MINIO_HOST") or 'localhost:9000'
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME") or 'songs'

# Key names for Redis
QUEUE_KEY = "toWorker"
LOGGING_KEY = "logging"

# Define info and debug keys based on the current node
infoKey = "{}.rest.info".format(platform.node())
debugKey = "{}.rest.debug".format(platform.node())

app = Flask(__name__)
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
minio_client = Minio(MINIO_HOST, access_key='rootuser', secret_key='rootpass123', secure=False)

def log_debug(message, key=debugKey):
    """Log a debug message to the Redis logging queue."""
    print("DEBUG:", message, file=sys.stdout)
    try:
        redis_client.lpush(LOGGING_KEY, f"{key}:{message}")
    except Exception as e:
        print(f"Error logging debug message: {e}", file=sys.stderr)

def log_info(message, key=infoKey):
    """Log an info message to the Redis logging queue."""
    print("INFO:", message, file=sys.stdout)
    try:
        redis_client.lpush(LOGGING_KEY, f"{key}:{message}")
    except Exception as e:
        print(f"Error logging info message: {e}", file=sys.stderr)


def generate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

@app.route('/apiv1/separate', methods=['POST'])
def separate():
    """
    Get the JSON base64 encoded data mp3 and queue the work for waveform separation. 
    Returns a unique identifier (songhash) that can later be 
    used to retrieve the separated tracks or delete them.
    """
    data = request.json
    
    song_name = data.get("song_name")
    log_info(f"Received: {song_name}")
    
    mp3_data_base64 = data.get("mp3")
    mp3_binary_data = base64.b64decode(mp3_data_base64)
    callback_url = data.get("callback")['url']
    songhash = generate_hash(mp3_data_base64)
    log_debug(f"Hash generated for {song_name} : {songhash}")

    task_data = {
        "songhash": songhash,
        "callback": callback_url
    }

    if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
        log_info(f"Create bucket {MINIO_BUCKET_NAME}")
        minio_client.make_bucket(MINIO_BUCKET_NAME)
    else:
        log_info(f"Bucket: {MINIO_BUCKET_NAME} exists")

    try:
        minio_client.put_object(bucket_name = MINIO_BUCKET_NAME, 
                                object_name = f'{songhash}/original.mp3',
                                data = io.BytesIO(mp3_binary_data), 
                                length = len(mp3_binary_data),
                                content_type = 'audio/mpeg')
        log_info(f"File placed in object store under bucket {MINIO_BUCKET_NAME}")
    except Exception as e:
        log_debug(f"Error : {e}")

    try:
        redis_client.lpush(QUEUE_KEY, jsonpickle.encode(task_data))
        log_info(f"File pushed to Redis queue")
    except Exception as e:
        log_debug(f"Error : {e}")
    return jsonify({"hash": songhash, "reason": "Song enqueued for separation"}), 200

@app.route('/apiv1/queue', methods=['GET'])
def queue():
    """
    Return the queued entries from the Redis database
    """
    queue_items = redis_client.lrange(QUEUE_KEY, 0, -1)
    task_hashes = [jsonpickle.decode(item).get("songhash") for item in queue_items]
    return jsonify({"queue": task_hashes}), 200

@app.route('/apiv1/track/<songhash>/<track>', methods=['GET'])
def get_track(songhash, track):  
    """
    Return the track - base, vocals, drums, other as a binary download
    """
    try:
        data = minio_client.get_object(MINIO_BUCKET_NAME, f"{songhash}/{track}.mp3")
        log_info("Track retrieved")
    except Exception as e:
        log_debug(f"Error : {e}")
    return send_file(io.BytesIO(data), 
                     mimetype="audio/mpeg", 
                     as_attachment=True)

@app.route('/apiv1/remove/<songhash>/<track>', methods=['DELETE'])
def remove_track(songhash, track):
    """
    Remove the corresponding track
    """
    try:
        minio_client.remove_object(MINIO_BUCKET_NAME, 
                               f"{songhash}/{track}.mp3")
        log_info("Track removed")
    except Exception as e:
        log_debug(f"Error : {e}")

if __name__ == '__main__':
    log_info("Flask app started")
    app.run(host='0.0.0.0', port=5050)
