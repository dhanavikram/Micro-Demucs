# Redis database

A single-pod deployment has been implemented that has a Redis database and a service called `redis` so that worker nodes can use DNS names to locate the instance. The provided deployment uses [the image provided by the Redis developers](https://hub.docker.com/_/redis).

No database tables have been created in advance -- that happens automatically when the `worker` starts using redis.

Redis does not have a persistent volume,but this causes problem in case a pod fails. This will be fixed in a future update and will be using persistent volumes.