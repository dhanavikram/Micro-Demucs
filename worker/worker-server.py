import os
import redis
import json
import requests
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

# Initialize Redis and Minio clients
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
minio_client = Minio(MINIO_HOST, access_key='rootuser', secret_key='rootpass123', secure=False)

# Define info and debug keys based on the current node
infoKey = "{}.worker.info".format(platform.node())
debugKey = "{}.worker.debug".format(platform.node())

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


def separate_track(songhash):
    input_path = f"/tmp/{songhash}.mp3"
    output_path = f"/tmp/output/"

    # Run DEMUCS to separate the tracks
    log_info(f"Running DEMUCS")
    try:
        os.system(f"python3 -m demucs.separate --out {output_path} --mp3 {input_path}")
        log_info("Track separated")
    except Exception as e:
        log_debug(f"Error {e}")

    # Upload the separated tracks back to Min.io
    parts = ["vocals", "drums", "bass", "other"]
    for part in parts:
        track_path = f"/tmp/output/mdx_extra_q/{songhash}/{part}.mp3"
        minio_client.fput_object(MINIO_BUCKET_NAME, f"{songhash}/{part}.mp3", track_path)
        log_info(f"Uploaded {part} track for {songhash} to Min.io")

def worker():
    # logger.info("Worker started. Listening for messages...")
    while True:
        request = redis_client.blpop(QUEUE_KEY, 0)[1]
        data = json.loads(request)

        # Retrieve song and model details
        songhash = data["songhash"]
        log_info(f"Request received for songhash: {songhash}")
        callback_url = data.get("callback")

        # Download the song from Min.io
        minio_client.fget_object(MINIO_BUCKET_NAME, f"{songhash}/original.mp3", f"/tmp/{songhash}.mp3")
        log_info(f"Downloaded {songhash}.mp3 for processing")

        # Process the track with DEMUCS
        separate_track(songhash)
        log_info("Track separated and objects stored.")

        # Notify the callback if provided
        if callback_url:
            try:
                requests.post(callback_url, json={"hash": songhash, "status": "completed"})
                log_info(f"Callback sent to {callback_url} for {songhash}")
            except requests.RequestException as e:
                pass
                log_debug(f"Failed to send callback to {callback_url}: {e}")

if __name__ == "__main__":
    log_info("Worker started")
    worker()
