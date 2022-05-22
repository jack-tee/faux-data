from dataclasses import dataclass
from distutils.core import setup

setup(name='faux-data',
      version='0.0.1',
      description='Generate fake data',
      author='jack-tee',
      author_email='10283360+jack-tee@users.noreply.github.com',
      packages=['faux_data'],
      entry_points={'console_scripts': ['faux=faux_data.cmd:main']})
