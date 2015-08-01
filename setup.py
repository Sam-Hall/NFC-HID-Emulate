from distutils.core import setup
from hidemu.main import __version__, __app_name__


setup(
    name=__app_name__,
    version=__version__,
    package_dir={'hidemu':'hidemu'},
    packages=['hidemu', 'hidemu.output', 'hidemu.reader'],
    requires=['pyscard'],
    url='',
    license='GPLv3',
    author='Sam Hall',
    author_email='sam.hall@cdu.edu.au',
    description=''
)
