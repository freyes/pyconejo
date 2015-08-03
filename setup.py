from setuptools import setup, find_packages

setup(name='pyconejo',
      version='0.1',
      description='generate messages',
      author='Felipe Reyes',
      author_email='freyes@tty.cl',
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'pyconejo-consumer = pyconejo.publisher:main',
            'pyconejo-publisher = pyconejo.publisher:main'
        ]
      }
)
