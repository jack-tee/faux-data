from distutils.core import setup

setup(name='datafaker',
      version='0.1',
      description='Generate fake data',
      author='JT',
      author_email='10283360+jack-tee@users.noreply.github.com',
      packages=['datafaker'],
      entry_points={'console_scripts': ['datafaker=datafaker.cmd:main']})
