'''Mikes wrapper for the visualizer???'''
from contextlib import contextmanager

import OpenGL
import OpenGL.GLUT
import OpenGL.GLU
import OpenGL.GL
import OpenGL.GL.framebufferobjects
import OpenGL.GL.shaders

__all__ = '''
    gl
    glu
    glut
'''.strip().split()


class ModuleProxy(object):
    
    def __init__(self, name, *modules):
        self._name = name
        self._modules = modules
        self._module = modules[0]
    
    def __getattr__(self, raw_name):

        # Constants.
        if raw_name.isupper():
            name = self._name.upper() + '_' + raw_name

        # Methods.
        else:
            name = raw_name.split('_')
            name = [x[0].upper() + x[1:] for x in name]
            name = self._name + ''.join(name)

        for module in self._modules:
            try:
                value = getattr(module, name)
            except AttributeError:
                continue
            else:
                setattr(self, raw_name, value)
                setattr(self, name, value)
                return value

        raise AttributeError(raw_name)


class GLProxy(ModuleProxy):
    
    @contextmanager
    def matrix(self):
        self._module.glPushMatrix()
        try:
            yield
        finally:
            self._module.glPopMatrix()
    
    @contextmanager
    def attrib(self, *args):
        mask = 0
        for arg in args:
            if isinstance(arg, basestring):
                arg = getattr(self._module, 'GL_%s_BIT' % arg.upper())
            mask |= arg
        self._module.glPushAttrib(mask)
        try:
            yield
        finally:
            self._module.glPopAttrib()
    
    def enable(self, *args, **kwargs):
        self._enable(True, args, kwargs)
        return self._apply_on_exit(self._enable, False, args, kwargs)
    
    def disable(self, *args, **kwargs):
        self._enable(False, args, kwargs)
        return self._apply_on_exit(self._enable, True, args, kwargs)
    
    def _enable(self, enable, args, kwargs):
        todo = []
        for arg in args:
            if isinstance(arg, basestring):
                arg = getattr(self._module, 'GL_%s' % arg.upper())
            todo.append((arg, enable))
        for key, value in kwargs.iteritems():
            flag = getattr(self._module, 'GL_%s' % key.upper())
            value = value if enable else not value
            todo.append((flag, value))
        for flag, value in todo:
            if value:
                self._module.glEnable(flag)
            else:
                self._module.glDisable(flag)
        
    def begin(self, arg):
        if isinstance(arg, basestring):
            arg = getattr(self._module, 'GL_%s' % arg.upper())
        self._module.glBegin(arg)
        return self._apply_on_exit(self._module.glEnd)
    
    @contextmanager
    def _apply_on_exit(self, func, *args, **kwargs):
        try:
            yield
        finally:
            func(*args, **kwargs)
        

gl = GLProxy('gl', OpenGL.GL, OpenGL.GL.framebufferobjects)
glu = ModuleProxy('glu', OpenGL.GLU)
glut = ModuleProxy('glut', OpenGL.GLUT)


class Shader(object):

    def __init__(self, vert_src, frag_src):
        self._vert = OpenGL.GL.shaders.compileShader(vert_src, gl.VERTEX_SHADER)
        self._frag = OpenGL.GL.shaders.compileShader(frag_src, gl.FRAGMENT_SHADER)
        self._prog = OpenGL.GL.shaders.compileProgram(self._vert, self._frag)
        self._locations = {}

    def use(self):
        gl.useProgram(self._prog)

    def unuse(self):
        pass
        # gl.useProgram(0)


