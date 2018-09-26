from setuptools import find_packages, setup

requirements = [
]
dev_requirements = [
    'pytest'
]

setup(
    name='sisu',
    packages=find_packages(),
    url='https://github.com/nmaswood/sisu-data-project',
    description='Intersection between two lists of integers',
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements
    }
)
