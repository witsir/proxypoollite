from setuptools import setup, find_packages

setup(
    name='proxypoollite',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'proxypoollite = proxypoollite.__main__:main'
        ]
    }
)