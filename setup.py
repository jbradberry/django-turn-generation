from distutils.core import setup

setup(
    name='django-turn-generation',
    version='0.1dev',
    author='Jeff Bradberry',
    author_email='jeff.bradberry@gmail.com',
    packages=['turngeneration'],
    license='LICENSE',
    description=("A Django app for specifying the timing of and triggering"
                 " turn generation for turn-based strategy games."),
)
