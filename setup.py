from setuptools import setup

setup(
    name='asciiclip',
    version='1.0.11',
    author='leinstay',
    author_email='leinstay@gmail.com',
    description='',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/leinstay/asciiclip',
    py_modules=['main'],
    packages=['app'],
    package_data={"app": ["*.ttf"], },
    install_requires=[
        "click",
        "moviepy",
        "pytube",
        "Pillow",
    ],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        asciiclip=main:cli
    '''
)
