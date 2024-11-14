# Micro Demucs
![separation](images/music_separation.png)
Music-Separation-as-a-service (MSaaS)

## Overview

Micro demucs is a backend for Music Separation as a services that uses Facebook's [demucs](https://github.com/facebookresearch/demucs) model. It is essentially a collection of  kubernetes clusters that provides a REST API for automatic music separation service and prepares the different tracks for retrieval. The reason for turning this into a micro-service is because it takes a long time to run the source separation (about 3-4x the running time of a song).

## Implementation

The `rest` folder provides necessary files for deploying a REST API that will accept API requests and handle queries concerning MP3's. The REST worker will queue tasks to workers using `redis` queues.

Rather than sending the large MP3 files through Redis, this implementation uses the Min.io object storage system (potentially another cloud storage in the future) to store the song contents ***and*** the output of the waveform separation. One benefit of an object store is that you can control access to those objects & direct the user to download the objects directly from *e.g.* S3 rather than relaying the data through your service. We're not going to rely on that feature.

The `worker` nodes will receive work requests to analyze MP3's and cache results in a cloud object store (Min.io in this demonstration).

For logging, this implementation uses [a simple python program `logs/log.py`](logs/logs.py) that connects to the `logging` key in database 0 of Redis using the `lpush`/`blpop` model. The logs can be monitored using `kubectl logs logs-<unique id for pod>`.

Each subdirectory contains more information in the appropriate README file.

### Port Forwarding

For local development, the following commands can be used to port-forward redis and minio components.

```
kubectl port-forward --address 0.0.0.0 service/redis 6379:6379 &
kubectl port-forward --namespace minio-ns svc/myminio-proj 9000:9000 &
kubectl port-forward --namespace minio-ns svc/myminio-proj 9001:9001
```
This forwards your Redis database to port 6379 on your computer and minio to local port 9000 on your computer. Then, your rest server & worker can connect to e.g. `localhost:6379` or `localhost:9000` while developing locally. 

To kill the port-forward processes one possible way would be to 

```bash
ps augxww | grep port-forward
kill -9 pid
```

### Sample Data
There is a program called `sample-requests.py` that make some sample requests, enabling the user to test all the rest functionalities. Keep in mind that processing an MP3 file takes a while - they also take a fair amount of memory.

## Credits

This project was done as a part of classwork for CSCI 5253 - Data Center Scale Computing.

The idea of this project and a starter code was provided by Professor [Dirk C Grunwald](https://github.com/dirkcgrunwald) and Professor [Eric Keller](https://github.com/eric-keller).