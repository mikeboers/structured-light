from __future__ import division

import argparse
import os

import cv, cv2
import numpy as np


def decode_gray(images):

    on = images[0]
    off = images[1]

    print 'decoding x'
    x, width = decode_axis(on, off, images[2::2])
    print 'decoding y'
    y, height = decode_axis(on, off, images[3::2])

    rgb = np.zeros(on.shape)
    rgb[...,2] = x / width
    rgb[...,1] = y / height
    return rgb


def remap(images):

    on = images[0]
    off = images[1]
    dist = distance(on, off)

    print 'decoding x'
    xcoords, width = decode_axis(on, off, images[2::2], 'x')
    cv2.imwrite('sandbox/xcoords.jpg', xcoords / width * 256)
    print np.max(xcoords), width
    print 'decoding y'
    ycoords, height = decode_axis(on, off, images[3::2], 'y')
    cv2.imwrite('sandbox/ycoords.jpg', ycoords / height * 256)
    print np.max(ycoords), width

    accum = np.zeros((width, height, 3))
    count = np.zeros((width, height, 3))
    print 'remapping'
    for i in xrange(on.shape[0]):
        print i / on.shape[0]
        for j in xrange(on.shape[1]):
            x = xcoords[i,j]
            y = ycoords[i,j]
            if dist[i,j] > 0.05:
                accum[height - y - 1, x] = on[i,j]
            # count[x,y] += 1

    return accum


def solve(images):

    on = images[0]
    off = images[1]
    dist = distance(on, off)

    print 'decoding x'
    xcoords, width = decode_axis(on, off, images[2::2], 'x')
    print 'decoding y'
    ycoords, height = decode_axis(on, off, images[3::2], 'y')

    cam_points = []
    proj_points = []

    for i in xrange(on.shape[0]):
        print i / on.shape[0]
        for j in xrange(on.shape[1]):
            x = xcoords[i,j]
            y = ycoords[i,j]
            if dist[i,j] > 0.25:
                cam_points.append((i, j))
                proj_points.append((height - y - 1, x))

    print len(cam_points), 'points'

    print 'finding fundamental matrix'
    cam_array = np.array(cam_points) / 1024 - 1
    proj_array = np.array(proj_points) / 1024 - 1
    F, status = cv2.findFundamentalMat(cam_array, proj_array, cv.CV_FM_RANSAC)

    print 'stereo rectify'
    cam_array = np.array(cam_points) / 1024 - 1
    proj_array = np.array(proj_points) / 1024 - 1
    res, H1, H2 = cv2.stereoRectifyUncalibrated(cam_array, proj_array, F, on.shape[:2])





def distance(high, low):
    return intensity(high - low)

def intensity(x):
    r = x[...,0]
    g = x[...,1]
    b = x[...,2]
    return np.sign(r) * r**2 + np.sign(g) * g**2 + np.sign(b) * b**2


def decode_axis(on, off, images, prefix='x'):

    avg = intensity((on + off) / 2)

    gray = np.zeros(shape=avg.shape, dtype='uint32')

    for i, image in reversed(list(enumerate(images))):

        bit = np.greater(intensity(image), avg)
        gray = (gray << 1) + bit.astype(int)
        cv2.imwrite('sandbox/bit-%s%d.jpg' % (prefix, i), bit * 256)

    mask = gray
    for i in xrange(len(images)):
        mask = mask >> 1
        gray = gray ^ mask

    return gray, 2**len(images)



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--skip', action='store_true')
    parser.add_argument('-o', '--output')
    parser.add_argument('-b', '--bits', type=int, default=11)
    parser.add_argument('-x', '--solve', action='store_true')
    parser.add_argument('images', nargs='+')
    args = parser.parse_args()

    paths = args.images
    if args.skip:
        paths = [args.images[i] for i in xrange(0, len(args.images), 2)]

    if args.bits:
        paths = paths[:2 + 2 * args.bits]

    images = []
    for path in paths:
        print 'reading {} ...'.format(path),
        image = cv2.imread(path)
        if image.dtype == np.uint8:
            image = image.astype(float) / 256
        if image.dtype != float:
            raise TypeError('image not convertable to float; got %r' % image.dtype)
        print image.shape, image.dtype
        images.append(image)


    if args.solve:
        solve(images)
    else:
        out = remap(images)
        out_path = args.output or (os.path.dirname(paths[0]) + '.jpg')
        print out_path
        cv2.imwrite(out_path, out * 256)
