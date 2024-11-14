# Waveform Separation Worker

The worker is just a python program that listens to the `toWorkers` redis key exchange, receives a message and retrieves the MP3 song to separate and performs the separation operation.

## Worker image
The worker uses the [Facebook DEMUCS](https://github.com/facebookresearch/demucs/blob/main/demucs/separate.py)
software. This is an open-source waveform separation library that has Python bindings. Installing demucs installs many packages, produces a ~3.5GB container image. It takes a while to upload that to e.g. the `docker.io` registry.

To save time, this implementation uses [an existing DEMUCS docker images](https://github.com/xserrat/docker-facebook-demucs) that is the container resulting from [this Dockerfile](https://github.com/xserrat/docker-facebook-demucs/blob/main/Dockerfile).

## Waveform Separation Analysis

The [DEMUCS Docker image](https://github.com/xserrat/docker-facebook-demucs) has directions on how to generate a song, which the worker code follows. The output files are also stored in `.mp3` format.

Initially, the `minio client` pulls the original song from the object store to `/tmp/` directory, which is then passed as an argument to the `demucs` program. 
Rather than trying to "call" the DEMUCS code from within my Python worker, I simply use the `os.system(....)` call to execute it as a separate program
The `demucs` program will leave the output in `/tmp/{songhash}` directory with four files -- one for each track.
For example, if processing a file from `/tmp/{songhash}.mp3` with output directory `/tmp/output`, the
output files are in `/tmp/output/mdx_extra_q/{songhash}/{part}.mp3` where `{songhash}` is the unique identifier for the original song, `mdx_extra_q` is the name of the model and `{part}` is one of `bass`, `drums`, `vocals` or `other`.

Then those files are placed in the Min.io storage system in the same bucket.

## Future Work

- Implement callback