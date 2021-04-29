# Description

This repo implements two methods of using phone camera as video input to opencv.

1. camera.py uses RTSP to transfer video stream to be captured by opencv. This method would also work for any ip camera.
2. The second method depends on https://obs.ninja/, which uses p2p technique to stream phone camera stream to the web. obs_ninja.py would then mirror what's on the website and extracting the frame to be processed by opencv