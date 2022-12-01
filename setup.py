from setuptools import setup

setup(
    name='asciiclip',
    version='1.0.1',
    author='leinstay',
    author_email='leinstay@gmail.com',
    description='CLI tool that applies an ASCII filter to video or image.',
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
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Multimedia :: Video :: Conversion",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Text Processing",
    ],
    entry_points='''
        [console_scripts]
        asciiclip=main:generate
    '''
)
