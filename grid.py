from __future__ import division

import sys
import time
import math
import random
import os
import itertools

from mygl import gl, glu, glut, Shader


class App(object):
    
    def __init__(self, argv):
    
        # Initialize GLUT and out render buffer.
        glut.init(argv)
        glut.initDisplayMode(glut.DOUBLE | glut.RGB)
    
        # Initialize the window.
        self.width = 1024
        self.height = 768
        glut.initWindowSize(self.width, self.height)
        glut.createWindow(argv[0])

        gl.clearColor(0, 0, 0, 1)
        
        self.offset_x = self.offset_y = 0
        self.base_size = 32
        self.layers = 3
        self.base_width = 1

        glut.reshapeFunc(self.reshape)
        glut.displayFunc(self.display)
        glut.keyboardFunc(self.keyboard)
        
    
    def keyboard(self, key, mx, my):

        if key in ('q', '\x1b'): # ESC
            exit(0)
        elif key == 'f':
            glut.fullScreen()

        elif key == 'a':
            self.base_size += 1
        elif key == 'z':
            self.base_size = max(2, self.base_size - 1)

        elif key == 's':
            self.layers += 1
        elif key == 'x':
            self.layers = max(1, self.layers - 1)

        elif key == 'd':
            self.base_width += 1
        elif key == 'c':
            self.base_width = max(1, self.base_width - 1)

        else:
            print 'unknown key %r at %s,%d' % (key, mx, my)

        glut.postRedisplay()
            
    def run(self):
        return glut.mainLoop()

    def reshape(self, width, height):
        """Called when the user reshapes the window."""

        self.width = width
        self.height = height
        
        print 'reshape to', width, height

        gl.viewport(0, 0, width, height)
        gl.matrixMode(gl.PROJECTION)
        gl.loadIdentity()
        gl.ortho(0, self.width, 0, self.height, -100, 100)
        gl.matrixMode(gl.MODELVIEW)
     


    def display(self):

        gl.clear(gl.COLOR_BUFFER_BIT)
        gl.color(1, 1, 1, 1)


        max_bits = max(int(math.log(self.width - 1, 2)), int(math.log(self.height - 1, 2))) + 1
        assert max_bits < 16

        for power in xrange(0, self.layers):

            size = self.base_size * 2**power
            gl.lineWidth(self.base_width + 2 * power)

            v = (power + 1) / float(self.layers)
            gl.color(v, v, v, 1)

            with gl.begin(gl.LINES):
                for x in xrange(size, self.width, size):
                    gl.vertex(x, 0, 0)
                    gl.vertex(x, self.height, 0)
                for y in xrange(size, self.height, size):
                    gl.vertex(0, y, 0)
                    gl.vertex(self.width, y, 0)

        glut.swapBuffers()

        
if __name__ == '__main__':
    app = App(sys.argv)
    exit(app.run())

    