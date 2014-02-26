import argparse
import os

import cv, cv2


parser = argparse.ArgumentParser()
parser.add_argument('-x', '--width', type=int, default=18)
parser.add_argument('-y', '--height', type=int, default=9)
parser.add_argument('-g', '--grids')
parser.add_argument('image', nargs='+')

args = parser.parse_args()

pattern_size = (args.width, args.height)

for path in args.image:

    print path
    image = cv2.imread(path)
    w, h = image.shape[:2]
    image = cv2.resize(image, (1024, int(1024 * h / w)))

    found, corners = cv2.findChessboardCorners(image, pattern_size, None, 0)
    print found, corners

    cv2.drawChessboardCorners(image, pattern_size, corners, found)

    if args.grids:
        new_path = os.path.join(args.grids, os.path.basename(path))
        cv2.imwrite(new_path, image)



