import cv2
import queue
import threading
import os
import time
import gluoncv
from gluoncv.data.transforms.presets.segmentation import test_transform
from gluoncv.utils.viz import get_color_pallete
import mxnet as mx
import numpy as np

class Model():
    
    def __init__(self):
        self._model = gluoncv.model_zoo.get_model('fcn_resnet101_voc', pretrained=True)
        self.ctx = mx.cpu(0)

    def __preprocess(self, frame):
        frame = mx.nd.array(frame)
        frame = test_transform(frame, self.ctx)
        return frame

    def __postprocess(self, predict):
        mask = get_color_pallete(predict, 'pascal_voc')
        return np.array(mask)

    def predict(self, frame):
        frame = self.__preprocess(frame)
        output = self._model.predict(frame)
        predict = mx.nd.squeeze(mx.nd.argmax(output, 1)).asnumpy()
        print(predict.shape)
        mask = self.__postprocess(predict)
        return mask

class StoppableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_evnet = threading.Event()
    
    def stop(self):
        self._stop_evnet.set()

    def stopped(self):
        return self._stop_evnet.is_set()

class ReceiveTask(StoppableThread):

    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)

    def run(self):
        print("start Reveive")
        while (self.cap.isOpened() and not self.stopped()):
            ret, frame = self.cap.read()
            if not ret:
                self.cap.release()
                self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
                continue
            q.put(frame)
        self.end_task()
    
    def end_task(self):
        self.cap.release()

q = queue.Queue()
model = Model()

def process_frame(frame):
    return model.predict(frame)

def Display():
    print("Start Displaying")
    while True:
        if not q.empty():
            frame = q.get()
            # frame = process_frame(frame)
            cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('User pressed Q, exiting')
            break
    p1.stop()
    p1.join()
    cv2.destroyAllWindows()
            
if __name__=='__main__':
    url = "rtsp://admin:12345@192.168.0.24:8554"
    p1 = ReceiveTask(url)
    p1.daemon = True
    p1.start()
    Display()

