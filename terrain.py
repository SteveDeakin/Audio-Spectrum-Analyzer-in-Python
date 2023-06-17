"""
This creates a 3D mesh with perlin noise to simulate
a terrain. The mesh is animated by shifting the noise
to give a "fly-over" effect.

If you don't have pyOpenGL or opensimplex, then:

    - conda install -c anaconda pyopengl
    - pip install opensimplex

"""

import sys

import PySide6.QtWidgets
import numpy as np
import pyqtgraph.opengl as gl
from PySide6.QtCore import QTimer
from opensimplex import OpenSimplex
from pyqtgraph.Qt import QtCore


class Terrain(object):
    def __init__(self):
        """
        Initialize the graphics window and mesh
        """

        # setup the view window
        self.timer = None
        self.app = PySide6.QtWidgets.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.setGeometry(0, 110, 1920/2, 1080/2)
        self.w.show()
        self.w.setWindowTitle('Terrain')
        self.w.setCameraPosition(distance=30, elevation=8)

        # constants and arrays
        self.nsteps = 1
        self.ypoints = range(-20, 22, self.nsteps)
        self.xpoints = range(-20, 22, self.nsteps)
        self.nfaces = len(self.ypoints)
        self.offset = 0

        # perlin noise object
        self.tmp = OpenSimplex(1)

        # create the veritices array
        verts = np.array([
            [
                x, y, 1.5 * self.tmp.noise2(x=n / 5, y=m / 5)
            ] for n, x in enumerate(self.xpoints) for m, y in enumerate(self.ypoints)
        ], dtype=np.float32)

        # create the faces and colors arrays
        faces = []
        colors = []
        for m in range(self.nfaces - 1):
            yoff = m * self.nfaces
            for n in range(self.nfaces - 1):
                faces.append([n + yoff, yoff + n + self.nfaces, yoff + n + self.nfaces + 1])
                faces.append([n + yoff, yoff + n + 1, yoff + n + self.nfaces + 1])
                colors.append([0, 0, 0, 0])
                colors.append([0, 0, 0, 0])

        faces = np.array(faces)
        colors = np.array(colors)

        # create the mesh item
        self.m1 = gl.GLMeshItem(
            vertexes=verts,
            faces=faces, faceColors=colors,
            smooth=False, drawEdges=True,
        )
        self.m1.setGLOptions('additive')
        self.w.addItem(self.m1)

    def update(self):
        """
        update the mesh and shift the noise each time
        """
        verts = np.array([
            [
                x, y, 2.5 * self.tmp.noise2(x=n / 5 + self.offset, y=m / 5 + self.offset)
            ] for n, x in enumerate(self.xpoints) for m, y in enumerate(self.ypoints)
        ], dtype=np.float32)

        faces = []
        colors = []
        for m in range(self.nfaces - 1):
            yoff = m * self.nfaces
            for n in range(self.nfaces - 1):
                faces.append([n + yoff, yoff + n + self.nfaces, yoff + n + self.nfaces + 1])
                faces.append([n + yoff, yoff + n + 1, yoff + n + self.nfaces + 1])
                colors.append([n / self.nfaces, 1 - n / self.nfaces, m / self.nfaces, 0.7])
                colors.append([n / self.nfaces, 1 - n / self.nfaces, m / self.nfaces, 0.8])

        faces = np.array(faces, dtype=np.uint32)
        colors = np.array(colors, dtype=np.float32)

        self.m1.setMeshData(
            vertexes=verts, faces=faces, faceColors=colors
        )
        self.offset -= 0.18

    def start(self):
        """
        get the graphics window open and setup
        """
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            PySide6.QtWidgets.QApplication.instance().exec()

    # noinspection PyUnresolvedReferences
    # connect is not found for some reason but still works fine in PyCharm and VSCode
    def animation(self):
        """
        calls the update method to run in a loop
        """
        timer = QTimer()
        timer.timeout.connect(self.update)
        timer.start(10)
        self.start()
        self.update()


if __name__ == '__main__':
    t = Terrain()
    t.animation()
