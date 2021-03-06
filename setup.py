from setuptools import setup, find_packages

setup(
    name='Instaseek',
    version='0.3.3',
    license='GNU-3.0',
    long_description=open('README.md').read(),
    packages=find_packages(),
    install_requires=[
        "colormath>=3.0",
        "imageio>=2.1.2",
        "matplotlib>=2.2.2",
        "networkx>=2.1",
        "opencv-python>=3.4.2.17",
        "pandas>=0.23.3",
        "psycopg2>=2.7.5",
        "scikit-learn>=0.19.2",
        "Pillow>=5.2.0",
        "scipy>=1.1.0",
        "regex>=2018.7.11",
        "tqdm>=4.11.2",
        "numpy>=1.15.0",
        "pip @ https://github.com/ValBerthe/Instagram-API-python/tarball/master"
    ],
)