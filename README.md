# ASCII Clip

[![PyPI](https://user-images.githubusercontent.com/8215580/204163662-d1475963-b56a-44c4-9d50-cf55bf8d4a17.svg)](https://pypi.org/project/asciiclip/)
[![license](https://user-images.githubusercontent.com/8215580/204163670-af0c2bfa-0ea0-44ac-bc4e-97971dcf12f0.svg)](https://github.com/leinstay/asciiclip/blob/master/LICENSE)

CLI tool that applies an ASCII filter to video or image. 

[![demo](https://user-images.githubusercontent.com/8215580/204165144-848c2fc8-9ea3-4fbb-be8d-142bb3210d48.png)](https://www.youtube.com/watch?v=lY-HOrYV_bk)

## Examples

Install latest version using pip:

```sh
python3 -m pip install asciiclip
```

Create an ASCII clip from YouTube video or local video

```sh
asciiclip -o https://www.youtube.com/watch?v=xxxxxxxx -d /dest/
asciiclip -o /from/clip.mp4 -d /to/ -s 10 -e 30
```

Create an ASCII image of a particular second from YouTube video or local video

```sh
asciiclip -o https://www.youtube.com/watch?v=xxxxxxxx -d /dest/ -r 120
asciiclip -o /from/clip.mp4 -d /to/ -r 5
```

Create an ASCII image from local image using custom ASCII character list

```sh
asciiclip -o /from/image.png -d /to/ -a \.\:\;\-\+\*\u\o\@
```

Create an ASCII clip using custom settings

```sh
asciiclip -o https://www.youtube.com/watch?v=xxxxxxxx -d /dest/ -a \.\:\;\-\+\*\u\o\@ -c 6 6 -fs 12 -q 720
```

## Installation

### Python package from PyPI

[pypi]: https://pypi.python.org/pypi/asciinema

asciiclip is available on [PyPI] and can be installed with pip (Python 3
with setuptools required):

```sh
python3 -m pip install asciiclip
```

Installing from [PyPI] is the recommended way of installation, which gives you the latest released version.

## Usage

When you run `asciiclip` with no arguments help message is displayed, listing all options.

Usage: asciiclip [OPTIONS]

Available options:

-   `-o, --source PATH`               - Link to YouTube video or path to image or video  *[required]*
-   `-d, --destination DIRECTORY`     - Output folder  *[required]*
-   `-f, --filename TEXT`             - Output file name  [default: ascii]
-   `-s, --start INTEGER`             - Used to trim video, sets the beginning point in seconds
-   `-e, --end INTEGER`               - Used to trim video, sets the ending point in seconds
-   `-r, --frame INTEGER`             - Turns the frame at a specified second of video into an image (-s/-e will be ignored)
-   `-t, --threads INTEGER RANGE`     - Number of threads used for video processing [default: 8; 1<=x<=32]
-   `-a, --chars TEXT`                - List of ASCII characters arranged from dark to light  [default: .;*uo]
-   `-p, --preset [720|1080]`         - A set of settings that will produce a 720p or 1080p output file (-c/-ft/-fs/-q will be ignored)
-   `-q, --sourcequality [360|480|720|1080]` - Height in pixels to which the video or image will be scaled down (the final result will be about [fontsize/chunk] times this value) [default: 360]
-   `-c, --chunk INTEGER RANGE...`    - Size of the rectangular area that will be consolidated to a single ASCII symbol [default: 2, 2; 0<=x<=128]
-   `-g, --gsv FLOAT RANGE...`        - RGB weights used when desaturating an image or video  [default: 0.299, 0.587, 0.114; 0<=x<=1]
-   `-c, --compression INTEGER RANGE` - PNG compression level  [default: 0; 0<=x<=9]
-   `-ft, --font FILE`                - Path to custom font  [default: moby.ttf]
-   `-fs, --fontsize INTEGER RANGE`   - Font size  [default: 6; 0<=x<=128]
-   `-fc, --fontcolor INTEGER RANGE`  - Font color  [default: 255, 255, 255; 0<=x<=255]
-   `--keepaspectratio`               - Preserves original aspect ratio, otherwise if the video is thinner than 16:9 bars will be added to the sides
-   `--mute`                          - Removes the audio track from the video
-   `--quiet`                         - Suppress all console messages
-   `--help`                          - Show this message and exit.
