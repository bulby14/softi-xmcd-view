from importlib.metadata import entry_points
from setuptools import setup, find_packages

setup(
    name="softi-xmcd-view",
    version=1.3,
    packages=find_packages(include=['xmcd_gui_logic_2', 'xmcd_gui', 'resourc', 'command_line', 'main_1']),
    scripts=['command_line'],
    install_requires = [
        'PyQt5',
        'scikit-image',
        'matplotlib',
        'pandas',
        'numpy',
        'scipy'
    ],
    entry_points={
        'console_scripts': ['softi-xmcd-view = command_line:main'],
    },
)

