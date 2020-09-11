import os

from modules.image.violation_detection.centroidtracker import CentroidTracker

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"  # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import time

import numpy as np
import pandas as pd
import tensorflow as tf

from modules import log, network, utils
from modules.base import Base
import cv2

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
graph_path = os.path.join(parent_folder_path, "frozen_inference_graph.pb")

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.io.gfile.GFile(graph_path, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.compat.v1.Session(
    config=config,
    graph=detection_graph)

image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
# Each box represents a part of the image where a particular object was detected.
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
# Each score represent how level of confidence for each of the objects.
# Score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

tag = "Violation detection"
log.i(tag, "loaded graph")


class Main(Base):
    def __init__(self, configs):
        self.configs = configs
        self.firstFrame = None

        if configs.get('line_start') is not None:
            self.line_start = tuple(configs.get('line_start'))
        else:
            self.line_start = (0, 4.9 / 10)

        if configs.get('line_end') is not None:
            self.line_end = tuple(configs.get('line_end'))
        else:
            self.line_end = (1, 6 / 10)

        self.violation_count = 0
        self.tracker = CentroidTracker(maxDisappeared=30)
        self.counted_ids = set()
        self.track_ids = set()

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
        df6 = df5.loc[df5['classes'].map(lambda x: True if x in [2, 3, 4, 6, 8] else False)]
        df7 = df6.loc[df6['scores'] > 0.5]
        # df8 = df7.loc[(df7['y_max'] - df7['y_min'])*(df7['x_max'] - df7['x_min']) < 0.5]
        df8 = df7.loc[df7['x_max'] - df7['x_min'] < 0.5]
        res_df = df8.loc[(df8['y_max'] - df8['y_min']) * (df8['x_max'] - df8['x_min']) > 0.01]

        rects = []
        h = input.shape[0]
        w = input.shape[1]
        for idx, row in res_df.iterrows():
            left = int(row['x_min'] * w)
            top = int(row['y_min'] * h)
            right = int(row['x_max'] * w)
            bottom = int(row['y_max'] * h)

            rects.append([left, top, right, bottom])

        rects = np.array(rects)
        rects = self.non_max_suppression_slow(rects, 0.3)

        objects = self.tracker.update(rects)
        has_violation = False

        targets = []

        # loop over the tracked objects
        for (objectID, centroid) in objects.items():
            center_x = centroid[0]
            center_y = centroid[1]

            y_t = (center_x * (self.line_end[1] - self.line_start[1]) / w + self.line_start[1]) * h

            # if under line add to track list
            if y_t <= center_y and objectID not in self.track_ids and objectID not in self.counted_ids:
                self.track_ids.add(objectID)
            # if appear in track list and above line so it's a violation
            elif center_y + 75 > y_t > center_y + 50 and objectID in self.track_ids and objectID not in self.counted_ids:
                self.violation_count += 1
                has_violation = True

                self.counted_ids.add(objectID)
                self.track_ids.discard(objectID)

                targets.append(centroid)

            # draw both the ID of the object and the centroid of the
            # object on the output frame
            # text = "Vehicle {}".format(objectID)
            # cv2.putText(input, text, (center_x - 10, center_y - 10),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            # cv2.circle(input, (center_x, center_y), 4, (0, 255, 0), -1)

        self.draw_result_on_frame(input, rects, targets)

        vehicle_count = abs(int(len(res_df.index)))
        if vehicle_count > 0:
            log.v(tag, "in", "{:.2f}".format((end_time - start_time) * 1000), "(ms) detected", vehicle_count,
                  "vehicle(s)")

        if has_violation:
            imencoded = cv2.imencode(".jpg", input)[1]

            timestamp = utils.current_milli_time()
            file = {'file': (
                'cam{}_{}.jpg'.format(self.configs['camera_id'], timestamp), imencoded.tostring(), 'image/jpeg',
                {'Expires': '0'}
            )}
            data = {
                "timestamp": timestamp,
                'camera_id': self.configs['camera_id'],
                'type': 'Red light violation'
            }
            network.Network.instance().post(
                self.configs['cloud_url'] + '/violation',
                files=file, data=data, timeout=5
            )

    def draw_result_on_frame(self, frame, rects, targets):
        # Display the results
        h = frame.shape[0]
        w = frame.shape[1]

        # draw line
        pt1 = (int(self.line_start[0] * w), int(self.line_start[1] * h))
        pt2 = (int(self.line_end[0] * w), int(self.line_end[1] * h))
        cv2.line(frame, pt1, pt2, (255, 0, 0), 3)

        cv2.putText(frame, "Violation count: " + str(self.violation_count), (5, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5,
                    (59, 101, 255), 1)

        for left, top, right, bottom in rects:
            color = (66, 161, 79)
            for target in targets:
                if left <= target[0] <= right and top <= target[1] <= bottom:
                    color = (0, 0, 255)
                    break

            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            # top = int(top * h)
            # right = int(right * w)
            # bottom = int(bottom * h)
            # left = int(left * w)

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Draw a label with a name below the face
            # cv2.rectangle(frame, (left, bottom - 28), (right, bottom), (0, 0, 255), cv2.FILLED)
            # font = cv2.FONT_HERSHEY_DUPLEX
            # cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.7, (255, 255, 255), 1)

    def non_max_suppression_slow(self, boxes, overlapThresh):
        # if there are no boxes, return an empty list
        if len(boxes) == 0:
            return []
        # initialize the list of picked indexes
        pick = []
        # grab the coordinates of the bounding boxes
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        # compute the area of the bounding boxes and sort the bounding
        # boxes by the bottom-right y-coordinate of the bounding box
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)

        # keep looping while some indexes still remain in the indexes
        # list
        while len(idxs) > 0:
            # grab the last index in the indexes list, add the index
            # value to the list of picked indexes, then initialize
            # the suppression list (i.e. indexes that will be deleted)
            # using the last index
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            suppress = [last]

            # loop over all indexes in the indexes list
            for pos in range(0, last):
                # grab the current index
                j = idxs[pos]
                # find the largest (x, y) coordinates for the start of
                # the bounding box and the smallest (x, y) coordinates
                # for the end of the bounding box
                xx1 = max(x1[i], x1[j])
                yy1 = max(y1[i], y1[j])
                xx2 = min(x2[i], x2[j])
                yy2 = min(y2[i], y2[j])
                # compute the width and height of the bounding box
                w = max(0, xx2 - xx1 + 1)
                h = max(0, yy2 - yy1 + 1)
                # compute the ratio of overlap between the computed
                # bounding box and the bounding box in the area list
                overlap = float(w * h) / area[j]
                # if there is sufficient overlap, suppress the
                # current bounding box
                if overlap > overlapThresh:
                    suppress.append(pos)
            # delete all indexes from the index list that are in the
            # suppression list
            idxs = np.delete(idxs, suppress)
            # return only the bounding boxes that were picked
        return boxes[pick]
