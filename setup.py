from os import path
from setuptools import setup, find_packages


here = path.dirname(path.abspath(__file__))
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()


setup(name='pyconejo',
      version='0.1',
      description='generate messages',
      author='Felipe Reyes',
      author_email='freyes@tty.cl',
      packages=find_packages(),
      long_description=long_description,
      entry_points={
        'console_scripts': [
            'pyconejo-consumer = pyconejo.consumer:main',
            'pyconejo-publisher = pyconejo.publisher:main',
            'pyconejo-rpc-server = pyconejo.rpc_server:main',
            'pyconejo-rpc-client = pyconejo.rpc_client:main',
        ]
      }
)
