from __future__ import division

import argparse
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
        glut.initDisplayMode(glut.DOUBLE | glut.RGB)
        # glut.initDisplayMode(2048)
    
        # Initialize the window.
        self.width = 1024
        self.height = 768
        glut.initWindowSize(self.width, self.height)
        glut.createWindow(argv[0])

        gl.clearColor(0, 0, 0, 1)
            
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

                float i = floor(axis > 0 ? gl_FragCoord.y: gl_FragCoord.x);
                float v = texture2D(texture, vec2(i / code_count, bit / bits)).r;
                gl_FragColor = vec4(v, v, v, 1.0);
            }

        ''')

        self.frame = 0

        parser = argparse.ArgumentParser()
        parser.add_argument('-g', '--gray', action='store_true')
        parser.add_argument('-b', '--binary', action='store_true')
        parser.add_argument('-r', '--grid', action='store_true')
        parser.add_argument('-i', '--info', action='store_true')
        parser.add_argument('-s', '--strobe', action='store_true')
        parser.add_argument('-f', '--fps', type=float, default=60.0)
        parser.add_argument('-n', '--noblack', action='store_true')
        args = parser.parse_args(argv[1:])

        self.stages = []
        if args.gray:
            self.stages.append(self.gray_stage)
        if args.binary:
            self.stages.append(self.binary_stage)
        if args.grid:
            self.stages.append(self.grid_stage)
        if args.info:
            self.stages.append(self.info_stage)
        if args.strobe:
            self.stages.append(self.strobe_stage)
        if not self.stages:
            parser.print_usage()
            exit(1)

        self.stepper = None

        glut.reshapeFunc(self.reshape)
        glut.displayFunc(self.display)
        glut.keyboardFunc(self.keyboard)
        
        self.frame_rate = args.fps
        self.no_black = args.noblack
        
    
    def keyboard(self, key, mx, my):
        if key in ('q', '\x1b'): # ESC
            exit(0)
        elif key == 'f':
            glut.fullScreen()
        elif key == ' ':
            self.scan()
            glut.postRedisplay()
        elif key == 'r':
            self.stepper = self.iter_scan()
            next(self.stepper)
        elif key == 'x':
            if not self.stepper:
                self.stepper = self.iter_scan()
            try:
                next(self.stepper)
            except StopIteration:
                self.stepper = None

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
        if delta < -0.004: # Window is 45deg of 1/30, or 1/240, or ~0.008.
            self.dropped = True
            print 'dropped frame; out by %dms' % abs(1000 * delta)
        elif delta > 0:
            time.sleep(delta)
        self.last_frame = next_frame

    def scan(self):

        sync_to = 0.1
        x = math.fmod(time.time(), sync_to)
        x = sync_to - x
        time.sleep(x)

        self.reset_timer()

        scan_iter = self.iter_scan()
        while True:

            try:
                next(scan_iter)
            except StopIteration:
                break

            self.tick()

            if not self.no_black:
                gl.clear(gl.COLOR_BUFFER_BIT)
                glut.swapBuffers()
                self.tick()

            if self.dropped:
                gl.color(1, 0, 0, 1)
                self.polyfill()
                glut.swapBuffers()
                time.sleep(0.5)
                return


    def iter_scan(self):

        stages = [stage() for stage in self.stages]
        for stage in stages:
            while True:

                gl.clear(gl.COLOR_BUFFER_BIT)
                gl.color(1, 1, 1, 1)

                try:
                    next(stage)
                except StopIteration:
                    break

                glut.swapBuffers()
                yield


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
        max_bits = int(math.ceil(max(math.log(self.width, 2), math.log(self.height, 2))))
        assert max_bits < 16
        assert self.width <= 2**max_bits
        assert self.height <= 2**max_bits
        assert self.width > 2**(max_bits-1) or self.height > 2**(max_bits-1)

        self.shader.use()
        self.shader.uniform1i('texture', texture)
        self.shader.uniform1f('bits', bits)
        self.shader.uniform1f('code_count', code_count)

        for bit in range(max_bits):
            self.shader.uniform1f('bit', bit)
            for axis in (0, 1):
                self.shader.uniform1i('axis', axis)
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

        for power in xrange(2, max_bits):
            gl.lineWidth(power - 1)
            self.grid(power)
            yield

        gl.color(1, 0, 1, 1)
        self.polyfill()
        yield

    def grid(self, power):
        size = 2**power
        with gl.begin(gl.LINES):
            for x in xrange(size, self.width, size):
                gl.vertex(x, 0, 0)
                gl.vertex(x, self.height, 0)
            for y in xrange(size, self.height, size):
                gl.vertex(0, y, 0)
                gl.vertex(self.width, y, 0)

    def info_stage(self):

        i = 0
        for power in xrange(1, 4):
            blocks = 2**power

            dx = self.width / float(blocks)
            dy = self.height / float(blocks)

            for x in xrange(blocks):
                for y in xrange(blocks):
                    
                    i = (i + 1) % 3
                    gl.color(int(i == 0), int(i == 1), int(i == 2), 1)
                    with gl.begin(gl.POLYGON):
                        gl.vertex(dx *  x     , dy *  y)
                        gl.vertex(dx * (x + 1), dy *  y)
                        gl.vertex(dx * (x + 1), dy * (y + 1))
                        gl.vertex(dx *  x     , dy * (y + 1))

                    if not i:
                        yield

        yield


        for power in xrange(1, 5):
            blocks = 2**power

            dx = self.width / float(blocks)
            dy = self.height / float(blocks)

            for i in xrange(blocks):

                with gl.begin(gl.POLYGON):
                    gl.vertex(dx * i, 0)
                    gl.vertex(dx * (i + 1), 0)
                    gl.vertex(dx * (i + 1), self.height)
                    gl.vertex(dx * i, self.height)
                yield

                with gl.begin(gl.POLYGON):
                    gl.vertex(0         , dy * i)
                    gl.vertex(self.width, dy * i)
                    gl.vertex(self.width, dy * (i + 1))
                    gl.vertex(0         , dy * (i + 1))
                yield

    def strobe_stage(self):
        while True:
            self.polyfill()
            yield
            yield

    def display(self):
        gl.clear(gl.COLOR_BUFFER_BIT)
        # gl.color(0, 0.0625, 0.125, 1)
        # self.polyfill()

        gl.color(0.25, 0.25, 0.0625, 1)
        for power in (1, 2):

            gl.lineWidth((3 - power)**3)

            dx = self.width // (2**power)
            dy = self.height // (2**power)

            with gl.begin(gl.LINES):
                for x in xrange(dx, self.width, dx):
                    gl.vertex(x, 0, 0)
                    gl.vertex(x, self.height, 0)
                for y in xrange(dy, self.height, dy):
                    gl.vertex(0, y, 0)
                    gl.vertex(self.width, y, 0)


        glut.swapBuffers()

        
if __name__ == '__main__':
    app = App(sys.argv)
    exit(app.run())

    