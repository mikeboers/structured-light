'''

Roughly following http://docs.opencv.org/trunk/doc/tutorials/calib3d/camera_calibration/camera_calibration.html

'''

import argparse
import os

import cv, cv2
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument('-x', '--width', type=int, default=18)
parser.add_argument('-y', '--height', type=int, default=9)
parser.add_argument('-g', '--grids')
parser.add_argument('image', nargs='+')

args = parser.parse_args()

pattern_size = (args.width, args.height)

base_object_points = []
for x in xrange(args.width):
    for y in xrange(args.height):
        base_object_points.append((x, y))


image_points = []

for image_i, path in enumerate(args.image):

    print path
    image = cv2.imread(path)
    w, h = image.shape[:2]
    image = cv2.resize(image, (2048, int(2048 * w / h)))

    if args.grids:
        new_path = os.path.join(args.grids, os.path.basename(path))
        cv2.imwrite(new_path, image)

    print 'finding rough corners'
    found, corners = cv2.findChessboardCorners(image, pattern_size, 0, cv.CV_CALIB_CB_ADAPTIVE_THRESH)
    # print found, corners

    # print 'finding fine corners'
    # TODO: move this back to the large frame.
    # cv2.cornerSubPix(image, corners, (5, 5))

    cv2.drawChessboardCorners(image, pattern_size, corners, found)

    if args.grids:
        new_path = os.path.join(args.grids, os.path.basename(path) + '.grid.jpg')
        cv2.imwrite(new_path, image)


    continue
    print 'calibrating'
    object_points = np.array([base_object_points for _ in xrange(image_i + 1)])
    image_points.append(corners)
    res = cv2.calibrateCamera(object_points, np.array(image_points), image.shape[:2])
    print res
    print




