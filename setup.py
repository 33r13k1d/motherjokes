from setuptools import (
    setup,
    find_packages,
)


with open('README.md', 'r') as fh:
    long_description = fh.read()


setup(
    name='motherjokes',
    version='0.1.1',
    description='Transform sentences into awesome jokes about your mother (in russian language for now)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/FFFEGO/motherjokes',
    author='Vladimir Kaigorodov',
    author_email='vladimir.kgrdv@gmail.com',
    packages=find_packages(exclude=['*.tests']),
    install_requires=[
        'pymorphy2==0.8',
        'mosestokenizer==1.0.0',
    ],
    extras_require={
        'dev': [
            'black',
            'pylint',
            'pytest',
            'pytest-cov',
            'coveralls',
        ]
    },
    python_requires='>=3.6',
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Processing :: Linguistic',
    ),
    license='MIT',
)
