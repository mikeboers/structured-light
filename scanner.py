from __future__ import division

import sys
import time
import math
import random
import os

from mygl import gl, glu, glut, Shader


graycodes = [(i >> 1) ^ i for i in xrange(4096)]
# graycodes = range(4096)
gray = [[graycodes[i] & (2**b) for i in xrange(4096)] for b in xrange(16)]


class App(object):
    
    def __init__(self, argv):
    
        # Initialize GLUT and out render buffer.
        glut.init(argv)
        glut.initDisplayMode(glut.DOUBLE | glut.RGBA | glut.DEPTH | glut.MULTISAMPLE)
        # glut.initDisplayMode(2048)
    
        # Initialize the window.
        self.width = 800
        self.height = 600
        glut.initWindowSize(self.width, self.height)
        glut.createWindow(argv[0])

        gl.clearColor(0, 0, 0, 1)
    
        # Turn on a bunch of OpenGL options.
        # gl.enable(gl.CULL_FACE)
        # gl.enable(gl.DEPTH_TEST)
        # gl.enable(gl.COLOR_MATERIAL)
        # gl.enable('blend')
        # gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA)
        # gl.enable('multisample')
        
        self.texture = gl.genTextures(1)
        gl.bindTexture(gl.TEXTURE_2D, self.texture)
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RED, 4096, 16, 0, gl.RED, gl.FLOAT, sum(gray, []))

        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)


        self.shader = Shader('''

            void main(void) {
                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
            }
        ''', '''

            uniform sampler2D texture;
            uniform int bit_idx;
            uniform int axis;

            void main(void) {

                int i = int(floor(axis > 0 ? gl_FragCoord.y : gl_FragCoord.x));
                float v = texture2D(texture, vec2(float(i) / 4096.0, float(bit_idx) / 16.0)).r;
                gl_FragColor = vec4(v, v, v, 1.0);
            }

        ''')

        self.frame = 0

        # Attach some GLUT event callbacks.
        glut.reshapeFunc(self.reshape)
        glut.displayFunc(self.display)
        glut.keyboardFunc(self.keyboard)
        
        self.frame_rate = 24.0 #12.0
        glut.timerFunc(int(1000 / self.frame_rate), self.timer, 0)
        
    
    def keyboard(self, key, mx, my):
        if key == '\x1b': # ESC
            exit(0)
        elif key == 'f':
            glut.fullScreen()
        elif key == ' ':
            self.frame += 1
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
        gl.ortho(0, 1, 0, 1, -100, 100)
        gl.matrixMode(gl.MODELVIEW)
        
    def timer(self, value):
        # self.frame += 1
        glut.postRedisplay()
        glut.timerFunc(int(1000 / self.frame_rate), self.timer, 0)

    def display(self):
    
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
        gl.enable('texture_2d')
        gl.enable('depth_test')
        gl.color(1, 1, 1, 1)

        max_bits = max(int(math.log(self.width, 2)), int(math.log(self.height, 2))) + 1
        assert max_bits < 16
        self.shader.use()
        self.shader.uniform1i('axis', self.frame // max_bits % 2)
        self.shader.uniform1i('bit_idx', self.frame % max_bits)

        # self.shader.uniform1i('texture', gl.TEXTURE0)

        with gl.begin('polygon'):
            gl.vertex(0, 0)
            gl.vertex(1, 0)
            gl.vertex(1, 1)
            gl.vertex(0, 1)

        glut.swapBuffers()

        
if __name__ == '__main__':
    app = App(sys.argv)
    exit(app.run())

    