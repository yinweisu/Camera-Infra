# Description

This repo implements two methods of using phone camera as video input to opencv.

1. camera.py uses RTSP to transfer video stream to be captured by opencv. This method would also work for any ip camera that supports RTSP.
2. The second method depends on https://obs.ninja/, which uses p2p technique to stream phone camera stream to the web. obs_ninja.py would then mirror what's on the website and extracting the frame to be processed by opencv

# Usage

### RTSP

1. To use RTSP method, one need to download an IP Camera app that's able to support RTSP. For example, LiveReporter on iOS, and IP Webcam on Android.
2. In the app, start a RTSP server 
3. update the RTSP address in camera.py and run the code

### OBS Ninja

1. Go to https://obs.ninja/ on your laptop and create a reusable invite link. 
2. Scan the qr code with your phone and start your camera
3. Copy the OBS Browser Source Link and use it as an argument to obs_ninja.py. For example ```python3 obs_ninja.py <URL>```

