from __future__ import division

import sys
import time
import math
import random
import os

from mygl import gl, glu, glut, Shader


class App(object):
    
    def __init__(self, argv):
    
        # Initialize GLUT and out render buffer.
        glut.init(argv)
        glut.initDisplayMode(glut.DOUBLE | glut.RGBA | glut.DEPTH | glut.MULTISAMPLE)
    
        # Initialize the window.
        self.width = 800
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
        

        self.fbo = gl.genFramebuffers(1)
        gl.bindFramebuffer(gl.FRAMEBUFFER, self.fbo)

        self.render_texture = gl.genTextures(1)
        gl.bindTexture(gl.TEXTURE_2D, self.render_texture)
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, self.width, self.height, 0, gl.RGB, gl.UNSIGNED_BYTE, 0)

        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR)

        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, self.render_texture, 0)


        gl.bindFramebuffer(gl.FRAMEBUFFER, 0)


        self.shader = Shader('''
            void main(void) {
                gl_Position = ftransform();
            }
        ''', '''
            void main(void) {
                gl_FragColor = vec4(gl_FragCoord.x / 400.0, gl_FragCoord.y / 300.0, 0.0, 1.0);
            }
        ''')

        # Attach some GLUT event callbacks.
        glut.reshapeFunc(self.reshape)
        glut.displayFunc(self.display)
        glut.keyboardFunc(self.keyboard)
        
        self.frame_rate = 24.0
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
        
    def timer(self, value):
        glut.postRedisplay()
        glut.timerFunc(int(1000 / self.frame_rate), self.timer, 0)

    def display(self):
    
        gl.bindFramebuffer(gl.FRAMEBUFFER, self.fbo)

        # Wipe the window.
        gl.disable('depth_test')
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)

        gl.loadIdentity()
        
        gl.disable('texture_2d')

        gl.color(1, 1, 1, 1)
        with gl.begin('polygon'):
            gl.vertex(0, 0)
            gl.vertex(400, 0)
            gl.vertex(400, 400)
            gl.vertex(0, 400)

        with gl.matrix():
            with gl.begin('line_strip'):
                for i in xrange(50):
                    gl.vertex(self.width * random.random(), self.height * random.random(), 0)

        

        gl.bindFramebuffer(gl.FRAMEBUFFER, 0)
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
        gl.enable('texture_2d')
        # gl.enable('depth_test')
        gl.color(1, 1, 1, 1)

        # self.shader.use()
        location = -1 # gl.getUniformLocation(self.shader._prog, "sampler")
        print location
        if location >= 0:
            gl.uniform1i(location, 0)

        with gl.begin('polygon'):
            gl.texCoord(0, 0)
            gl.vertex(0, 0)
            gl.texCoord(1, 0)
            gl.vertex(self.width / 2, 0)
            gl.texCoord(1, 1)
            gl.vertex(self.width / 2, self.height / 2)
            gl.texCoord(0, 1)
            gl.vertex(0, self.height / 2)

        # self.shader.unuse()

        glut.swapBuffers()

        
if __name__ == '__main__':
    app = App(sys.argv)
    exit(app.run())

    