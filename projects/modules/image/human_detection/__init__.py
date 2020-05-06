import os
import time

import numpy as np
import pandas as pd
import tensorflow as tf

from modules.base import Filter

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
graph_path = os.path.join(parent_folder_path, "frozen_inference_graph.pb")

# self.detection_graph = tf.Graph()
# with self.detection_graph.as_default():
#     od_graph_def = tf.compat.v1.GraphDef()
#     with tf.io.gfile.GFile(graph_path, 'rb') as fid:
#         serialized_graph = fid.read()
#         od_graph_def.ParseFromString(serialized_graph)
#         tf.import_graph_def(od_graph_def, name='')
# self.sess = tf.compat.v1.Session(graph=self.detection_graph)
#
# self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
# # Each box represents a part of the image where a particular object was detected.
# self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
# # Each score represent how level of confidence for each of the objects.
# # Score is shown on the result image, together with the class label.
# self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
# self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
# self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.io.gfile.GFile(graph_path, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
sess = tf.compat.v1.Session(graph=detection_graph)

image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
# Each box represents a part of the image where a particular object was detected.
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
# Each score represent how level of confidence for each of the objects.
# Score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
num_detections = detection_graph.get_tensor_by_name('num_detections:0')


class Main(Filter):
    def __init__(self, configs):
        self.configs = configs

    def run(self, input: np.ndarray):
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(input, axis=0)

        # Actual detection.
        start_time = time.time()
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: image_np_expanded})
        end_time = time.time()

        df = pd.DataFrame(boxes.reshape(100, 4), columns=['y_min', 'x_min', 'y_max', 'x_max'])
        df1 = pd.DataFrame(classes.reshape(100, 1), columns=['classes'])
        df2 = pd.DataFrame(scores.reshape(100, 1), columns=['scores'])
        df5 = pd.concat([df, df1, df2], axis=1)
        df6 = df5.loc[df5['classes'] == 1]
        df7 = df6.loc[df6['scores'] > 0.50]

        people_count = int(len(df7.index)) if int(len(df7.index)) > 0 else 0
        print("Human detection: detected ", people_count, " people in ",
              "{:.2f}".format((end_time - start_time) * 1000), " ms")
        return True if people_count > 0 else False
