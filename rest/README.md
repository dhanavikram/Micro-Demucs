# REST API and interface

Micro Demucs consists of a rest-server deployment, service and ingress that makes the specified REST api externally available.

`rest-server.py` implements a Flask server that responds to the routes below. 

+ /apiv1/separate[POST] - get the JSON base64 encoded data `mp3` and
queue the work for waveform separation. The REST server returns a unique identifier (`songhash`) that can later be used to retrieve the separated tracks or delete them.
+ /apiv1/queue[GET] - dump the queued entries from the Redis database
+ /apiv1/track/<songhash>/track [GET] - retrieve the track ( any of `base.mp3`, `vocals.mp3`, `drums.mp3`, `other.mp3`) as a binary download. 
+ /apiv1/remove/<songhash>/track [GET] - remove the corresponding track.

Sample queries using the Python `requests` API are in `sample-requests.py` and `short-sample-requests.py`. Refer to those examples for input format.

Sample outputs using the examples in `sample-requests.py` are below.
```
Response to http://localhost:500/apiv1/separate => {
        "hash": "e5f013b19e55e5b7354eaf303c86b2b93f1d2847d8c9fa58c77a0add", 
        "reason": "Song enqueued for separation"
}
Response to http://localhost:5000/apiv1/queue request is
{
    "queue": [
        "e5f013b19e55e5b7354eaf303c86b2b93f1d2847d8c9fa58c77a0add"
    ]
}
```

### Working

There exists two Redis list data types - one to send data to the worker & another for logging. Redis uses numerical database numbers and number 0 is the default database. Each database is a "key-value" store meaning you can specify different keys for the worker queue (`toWorker` is a good key) and logging (`logging`).

The REST server gets the data and generates a hash for it. It then sends the hash value to the `toWorker` queue and uploads the decoded mp3 data to Min.io. The data can be fetched again by the `worker` during its runtime.

The entire mp3 data received in string format is used for hash generation (SHA256) and is again converted into a byte stream format to upload to Min.io in a bucket called "songs" which can be modified.

## Future work

- Implement callback
- Implement gRPC instead of REST for interprocess communication