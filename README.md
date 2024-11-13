# Micro Demucs
![separation](images/music_separation.png)
Music-Separation-as-a-service (MSaaS)

## Overview

Micro demucs is a backend for Music Separation as a services that uses Facebook's [demucs](https://github.com/facebookresearch/demucs) model. It is essentially a collection of  kubernetes clusters that provides a REST API for automatic music separation service and prepares the different tracks for retrieval. The reason for turning this into a micro-service is because it takes a long time to run the source separation (about 3-4x the running time of a song).