from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
setup(
    name='asciiclip',
    version='1.0.0',
    author='leinstay',
    author_email='leinstay@gmail.com',
    license='MIT License',
    description='TODO',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/leinstay/asciiclip',
    py_modules=['app', 'src'],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        asciiclip=app:cli
    '''
)
