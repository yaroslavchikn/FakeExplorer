from setuptools import setup

setup(
    name="FakeExplorer",
    version="1.0.0",
    py_modules=["main"],
    install_requires=["PyQt5>=5.15.0"],
    entry_points={
        'console_scripts': [
            'fake-explorer=main:main',
        ],
    },
)
