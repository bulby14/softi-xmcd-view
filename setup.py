from importlib.metadata import entry_points
from setuptools import setup, find_packages

setup(
    name="SoftiMAX_XMCD_plotter",
    version=0.3,
    packages=find_packages(include=['xmcd_gui_logic_2', 'xmcd_gui', 'resourc']),
    install_requires = [
        'PyQt5',
        'scikit-image',
        'matplotlib',
        'pandas',
        'numpy',
        'scipy'
    ],
    entry_points={
        'console_scripts' : ['softimax_xmcd_plotter=plotter_1:main']
    }
)

