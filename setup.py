from importlib.metadata import entry_points
from setuptools import setup, find_packages

setup(
    name="softi-xmcd-view",
    version=1.1,
    packages=find_packages(include=['main_1', 'xmcd_gui_logic_2', 'xmcd_gui', 'resourc']),
    install_requires = [
        'PyQt5',
        'scikit-image',
        'matplotlib',
        'pandas',
        'numpy',
        'scipy'
    ],
    entry_points={
        'console_scripts': ['softi-xmcd-view = main_1'],
    },
)

