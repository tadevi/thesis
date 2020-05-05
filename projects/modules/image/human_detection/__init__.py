import numpy as np
import pandas as pd
import tensorflow as tf
import os

from modules.base import Filter


class Main(Filter):
    def __init__(self, configs):
        self.configs = configs

        parent_folder_path = os.path.abspath(os.path.dirname(__file__))
        graph_path = os.path.join(parent_folder_path, "frozen_inference_graph.pb")

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(graph_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

    def run(self, input: np.ndarray):
        with self.detection_graph.as_default():
            with tf.compat.v1.Session(graph=self.detection_graph) as sess:
                dimg = input
                # cv2.imwrite(path + datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f') + '.jpg', dimg)
                image_np = dimg
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
                # Each box represents a part of the image where a particular object was detected.
                boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
                # Actual detection.
                (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})

                df = pd.DataFrame(boxes.reshape(100, 4), columns=['y_min', 'x_min', 'y_max', 'x_max'])
                df1 = pd.DataFrame(classes.reshape(100, 1), columns=['classes'])
                df2 = pd.DataFrame(scores.reshape(100, 1), columns=['scores'])
                df5 = pd.concat([df, df1, df2], axis=1)
                df6 = df5.loc[df5['classes'] == 1]
                df7 = df6.loc[df6['scores'] > 0.50]

                people_count = int(len(df7.index)) if int(len(df7.index)) > 0 else 0
                print("Human detection: detected ", people_count, " people")
                return True if people_count > 0 else False
