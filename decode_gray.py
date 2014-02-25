from __future__ import division

import argparse

import cv2
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
    parser.add_argument('-o', '--output', default='coord.jpg')
    parser.add_argument('images', nargs='+')
    args = parser.parse_args()

    images = []
    for path in args.images:
        print 'reading {} ...'.format(path),
        image = cv2.imread(path)
        if image.dtype == np.uint8:
            image = image.astype(float) / 256
        if image.dtype != float:
            raise TypeError('image not convertable to float; got %r' % image.dtype)
        print image.shape, image.dtype
        images.append(image)

    out = remap(images)
    cv2.imwrite(args.output, out * 256)
