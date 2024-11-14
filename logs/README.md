# Logging README

Micro Demucs comes with a Dockerfile and deployment for a logging service.

The logging service uses the [Redis list data-types](https://redis.io/docs/data-types/lists/) using [`lpush`](https://redis.io/docs/data-types/lists/#basic-commands) to add work to the queue and [`blpop` blocking pop](https://redis.io/docs/data-types/lists/#blocking-commands) to wait for work and remove it for processing.

At each step of the processing, the REST and worker code logs debug information using this logging infrastructure. The REST and Worker servers send messages using `lpush`. The following code shows how to do that:

There are `INFO` and `DEBUG` messages which help with check the flow and errors in code. The following code is used in REST and worker applications.

```
redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    redisClient.lpush('logging', f"{debugKey}:{message}")

def log_info(message, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    redisClient.lpush('logging', f"{infoKey}:{message}")
```

and the logging server would wait for messages using the "blocking" `blpop` method:
