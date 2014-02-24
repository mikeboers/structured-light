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
        self.width = 1024
        self.height = 768
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
            self.gray_stage,
            self.binary_stage,
            self.grid_stage,
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
        
    
    def keyboard(self, key, mx, my):
        if key == '\x1b': # ESC
            exit(0)
        elif key == 'f':
            glut.fullScreen()
        elif key == ' ':
            self.scan()
        else:
            print 'unknown key %r at %s,%d' % (key, mx, my)
            
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
       
    def reset_timer(self):
        self.last_frame = time.time()
        self.dropped = False

    def tick(self):
        next_frame = self.last_frame + 1.0 / self.frame_rate
        delta = next_frame - time.time()
        if delta < 0:
            self.dropped = True
            print 'dropped frame; out by %dms' % abs(delta)
        else:
            time.sleep(delta)
        self.last_frame = next_frame

    def scan(self):

        self.reset_timer()

        stages = [stage() for stage in self.stages]
        for stage in stages:
            while True:

                gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
                gl.color(1, 1, 1, 1)

                try:
                    next(stage)
                except StopIteration:
                    break

                glut.swapBuffers()
                self.tick()

                gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
                glut.swapBuffers()
                self.tick()

                if self.dropped:
                    gl.color(1, 0, 0, 1)
                    self.polyfill()
                    glut.swapBuffers()
                    time.sleep(0.5)
                    return

    def polyfill(self):
        with gl.begin('polygon'):
            gl.vertex(0, 0)
            gl.vertex(self.width, 0)
            gl.vertex(self.width, self.height)
            gl.vertex(0, self.height)

    def gray_stage(self, texture=0):

        if not texture:
            gl.color(0, 1, 0, 1)
        else:
            gl.color(0, 1, 1, 1)
        self.polyfill()
        yield

        gl.color(1, 1, 1, 1)
        self.polyfill()
        yield

        yield

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

        gl.color(1, 0, 1, 1)
        self.polyfill()
        yield

    def binary_stage(self):
        return self.gray_stage(1)

    def grid_stage(self):

        gl.color(0, 0, 1, 1)
        self.polyfill()
        yield

        max_bits = max(int(math.log(self.width - 1, 2)), int(math.log(self.height - 1, 2))) + 1
        assert max_bits < 16

        for power in xrange(4, max_bits):
            size = 2**power
            gl.lineWidth(2)
            with gl.begin(gl.LINES):
                for x in xrange(0, self.width, size):
                    gl.vertex(x, 0, 0)
                    gl.vertex(x, self.height, 0)
                for y in xrange(0, self.height, size):
                    gl.vertex(0, y, 0)
                    gl.vertex(self.width, y, 0)
            yield

        gl.color(1, 0, 1, 1)
        self.polyfill()
        yield

    def display(self):
    
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
        gl.color(0.25, 0.25, 0.25, 1)
        self.polyfill()
        glut.swapBuffers()

        
if __name__ == '__main__':
    app = App(sys.argv)
    exit(app.run())

    