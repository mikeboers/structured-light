from __future__ import division

import sys
import time
import math
import random
import os
import itertools

from mygl import gl, glu, glut, Shader


bits = 12
code_count = 2**bits
gray_codes = [(i >> 1) ^ i for i in xrange(code_count)]
gray_bits = [[gray_codes[i] & (2**b) for i in xrange(code_count)] for b in xrange(bits)]

binary_codes = range(code_count)
binary_bits = [[binary_codes[i] & (2**b) for i in xrange(code_count)] for b in xrange(bits)]


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
        
        self.gray_texture = gl.genTextures(1)
        gl.activeTexture(gl.TEXTURE0)
        gl.bindTexture(gl.TEXTURE_2D, self.gray_texture)
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RED, code_count, bits, 0, gl.RED, gl.FLOAT, sum(gray_bits, []))
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)

        self.binary_texture = gl.genTextures(1)
        gl.activeTexture(gl.TEXTURE1)
        gl.bindTexture(gl.TEXTURE_2D, self.binary_texture)
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RED, code_count, bits, 0, gl.RED, gl.FLOAT, sum(binary_bits, []))
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)

        self.shader = Shader('''

            void main(void) {
                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
            }
        ''', '''

            uniform float bits, code_count;
            uniform sampler2D texture;
            uniform float bit;
            uniform int axis;

            void main(void) {

                float i = floor(axis > 0 ? gl_FragCoord.y : gl_FragCoord.x);
                float v = texture2D(texture, vec2(i / code_count, bit / bits)).r;
                gl_FragColor = vec4(v, v, v, 1.0);
            }

        ''')

        self.frame = 0

        self.stages = [
            self.start_stage,
            self.gray_stage,
            self.separator,
            self.binary_stage,
            self.end_stage,
        ]
        self.stagesx = [
            self.separator,
        ]
        self.stage_iter = None

        self.last_frame = 0
        self.blank = True
        self.dropped = False

        # Attach some GLUT event callbacks.
        glut.reshapeFunc(self.reshape)
        glut.displayFunc(self.display)
        glut.keyboardFunc(self.keyboard)
        
        self.frame_rate = 60.0
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


        next_frame = self.last_frame + 1.0 / self.frame_rate
        delta = int(1000 * (next_frame - time.time()))

        if delta < 0:
            print 'dropped frame; out by %dms' % abs(delta)
            self.dropped = True
            self.last_frame = time.time() + 1.0 / self.frame_rate
        else:
            self.last_frame = next_frame

        glut.postRedisplay()
        glut.timerFunc(max(0, delta), self.timer, 0)

    def polyfill(self):
        with gl.begin('polygon'):
            gl.vertex(0, 0)
            gl.vertex(1, 0)
            gl.vertex(1, 1)
            gl.vertex(0, 1)

    def start_stage(self):

        self.polyfill()
        yield
        self.polyfill()
        yield

        gl.color(0.0, 0.0, 0.0, 1.0)
        self.polyfill()
        yield

    def separator(self):

        self.polyfill()
        yield
        gl.color(0.0, 0.0, 0.0, 1.0)
        self.polyfill()
        yield

    def end_stage(self):

        gl.color(0.0, 0.0, 0.0, 1.0)
        self.polyfill()
        yield
        gl.color(0.0, 0.0, 0.0, 1.0)
        self.polyfill()
        yield


    def gray_stage(self, texture=0):
        print 'gray_stage', texture

        # Subtract 1 so that 1024 only takes 9 bits.
        max_bits = max(int(math.log(self.width - 1, 2)), int(math.log(self.height - 1, 2))) + 1
        assert max_bits < 16
        self.shader.use()
        self.shader.uniform1i('texture', texture)
        self.shader.uniform1f('bits', bits)
        self.shader.uniform1f('code_count', code_count)

        for axis in (0, 1):
            self.shader.uniform1i('axis', axis)
            for bit in range(max_bits):
                self.shader.uniform1f('bit', bit)
                self.polyfill()
                yield

        self.shader.unuse()

    def binary_stage(self):
        return self.gray_stage(1)

    def display(self):
    
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)

        if not self.blank:
            if self.dropped:
                gl.color(1, 0, 0, 1)
                self.dropped = False
            else:
                gl.color(1, 1, 1, 1)

        while not self.blank:

            if not self.stage_iter:
                self.stage_iter = itertools.chain(*(stage() for stage in self.stages))
            try:
                next(self.stage_iter)
            except StopIteration:
                self.stage_iter = None
            else:
                break

        self.blank = not self.blank

        glut.swapBuffers()

        
if __name__ == '__main__':
    app = App(sys.argv)
    exit(app.run())

    