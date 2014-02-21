from __future__ import division

import sys
import time
import math
import random
import os

from mygl import gl, glu, glut
from svg import SVG


class App(object):
    
    def __init__(self, argv):
    
        # Initialize GLUT and out render buffer.
        glut.init(argv)
        glut.initDisplayMode(glut.DOUBLE | glut.RGBA | glut.DEPTH | glut.MULTISAMPLE)
    
        # Initialize the window.
        self.width = 600
        self.height = 600
        glut.initWindowSize(self.width, self.height)
        glut.createWindow(argv[0])

        gl.clearColor(0, 0, 0, 1)
    
        # Turn on a bunch of OpenGL options.
        gl.enable(gl.CULL_FACE)
        gl.enable(gl.DEPTH_TEST)
        gl.enable(gl.COLOR_MATERIAL)
        gl.enable('blend')
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA)
        gl.enable('multisample')
        
        # Attach some GLUT event callbacks.
        glut.reshapeFunc(self.reshape)
        glut.displayFunc(self.display)
        glut.keyboardFunc(self.keyboard)
        
        self.frame_rate = 24.0

        self.objects = [SVG(x) for x in argv[1:]]

        # Schedule the first frame.
        glut.timerFunc(int(1000 / self.frame_rate), self.timer, 0)
        
    
    def keyboard(self, key, mx, my):
        if key == '\x1b': # ESC
            exit(0)
        elif key == 'f':
            glut.fullScreen()
        else:
            print 'unknown key %r at %s,%d' % (key, mx, my)
            
    def run(self):
        return glut.mainLoop()

    def reshape(self, width, height):
        """Called when the user reshapes the window."""
        self.width = width
        self.height = height
        
        gl.viewport(0, 0, width, height)
        gl.matrixMode(gl.PROJECTION)
        gl.loadIdentity()
        gl.ortho(0, width, 0, height, -100, 100)
        gl.matrixMode(gl.MODELVIEW)
        
        self.setup_lighting()
    
    def setup_lighting(self):
        gl.enable('lighting')
        gl.enable('light0')
        gl.light(gl.LIGHT0, gl.AMBIENT, (0.5, 0.5, 0.5, 1.0))
        gl.light(gl.LIGHT0, gl.DIFFUSE, (0.8, 1.0, 0.8, 1.0))
        
        gl.light(gl.LIGHT0, gl.CONSTANT_ATTENUATION, 0.8)
        gl.light(gl.LIGHT0, gl.LINEAR_ATTENUATION, 0.5)
        
        gl.light(gl.LIGHT0, gl.POSITION, (0, 1, 1, 0))
        
        
    def timer(self, value):
 
        glut.postRedisplay()

        # Schedule the next frame.
        glut.timerFunc(int(1000 / self.frame_rate), self.timer, 0)

    def step(self):
        
        # Signal that we want a redraw.
        glut.postRedisplay()
       

    def display(self):
    
        # Wipe the window.
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)

        gl.loadIdentity()
        
        with gl.matrix():
            with gl.begin('line_strip'):
                for i in xrange(50):
                    gl.vertex(self.width * random.random(), self.height * random.random(), 0)

        for obj in self.objects:
            with gl.matrix():
                gl.translate(10, 10, 0)
                gl.scale(0.9, 0.9, 0.9)
                obj.draw()

        glut.swapBuffers()

        
if __name__ == '__main__':
    app = App(sys.argv)
    exit(app.run())

    