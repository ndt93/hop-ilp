from distutils.core import setup, Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize([Extension(name='solver',
                                     sources=['solver.pyx']),
                           Extension(name='utils',
                                     sources=['utils.pyx'])],
                          include_path=['.'])
)
