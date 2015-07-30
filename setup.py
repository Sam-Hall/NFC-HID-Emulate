from distutils.core import setup

setup(
    name='ACR122-HID-Emulate',
    version='0.2',
    package_dir={'hidemu':'hidemu'},
    packages=['hidemu', 'hidemu.output', 'hidemu.reader'],
    requires=['pyscard'],
    url='',
    license='GPLv3',
    author='',
    author_email='',
    description=''
)
