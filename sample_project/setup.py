from setuptools import setup, find_packages

setup(
    name='sample-app',
    version='0.1dev',
    author='Jeff Bradberry',
    author_email='jeff.bradberry@gmail.com',
    packages=find_packages(),
    entry_points={'turngeneration.plugins':
                  ["sample_app = sample_app.plugins:TurnGeneration"]},
    license='LICENSE',
    description=("A Django app."),
)
