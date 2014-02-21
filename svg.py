import re
import xml.etree.ElementTree as etree
from types import GeneratorType

from mygl import gl


pixels_re = re.compile(r'^(\d+)px$')


class next_on_exit(object):

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        pass

    def __exit__(self, *exc):
        if isinstance(self.obj, GeneratorType):
            next(self.obj)


class SVG(object):

    def __init__(self, path):
        self.path = path
        self.tree = etree.parse(path)
        self.root = self.tree.getroot()

        self.width = int(pixels_re.match(self.root.attrib['width']).group(1))
        self.height = int(pixels_re.match(self.root.attrib['height']).group(1))

    def draw(self):

        with gl.begin('line_loop'):
            gl.color(1, 1, 1, 1)
            gl.vertex(0, 0, 0)
            gl.vertex(self.width, 0, 0)
            gl.vertex(self.width, self.height, 0)
            gl.vertex(0, self.height, 0)

        self.visit(self.root)

    def visit(self, node):

        tag = node.tag.split('}')[-1]

        func = getattr(self, 'visit_' + tag, None)
        with next_on_exit(func and func(node)):
            for child in node:
                self.visit(child)

    def visit


class Node(object):

    types = {}

    def __init__(self, node):
        pass




