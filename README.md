# ASCII Clip

Command-line tool that applies an ASCII filter to a video or an image. It takes a local file or a YouTube link, scales it down, maps blocks of pixels to characters by brightness and renders the result back into a video with the original audio, or into a PNG.

[![Demo on YouTube](https://user-images.githubusercontent.com/8215580/204165144-848c2fc8-9ea3-4fbb-be8d-142bb3210d48.png)](https://www.youtube.com/watch?v=lY-HOrYV_bk)

## Requirements

Python 3.7 or newer. The dependencies (`click`, `moviepy`, `pytube`, `Pillow`) are installed by pip.

## Installation

```sh
python3 -m pip install asciiclip
```

Or from source:

```sh
git clone https://github.com/leinstay/asciiclip.git
cd asciiclip
python3 -m pip install .
```

## Usage

Make an ASCII clip from a YouTube video or a local video, optionally trimmed to seconds 10 to 30:

```sh
asciiclip -o https://www.youtube.com/watch?v=xxxxxxxx -d /dest/
asciiclip -o /from/clip.mp4 -d /to/ -s 10 -e 30
```

Render a single frame at a given second as an image:

```sh
asciiclip -o https://www.youtube.com/watch?v=xxxxxxxx -d /dest/ -r 120
asciiclip -o /from/clip.mp4 -d /to/ -r 5
```

Convert an image with a custom character ramp, dark to light:

```sh
asciiclip -o /from/image.png -d /to/ -a ".:;-+*uo@"
```

Make a clip with custom quality, chunk and font settings:

```sh
asciiclip -o https://www.youtube.com/watch?v=xxxxxxxx -d /dest/ -a ".:;-+*uo@" -q 1080 -h 6 6 -fs 6
```

## Options

Running `asciiclip` without arguments prints this list.

| Option | Default | Meaning |
|---|---|---|
| `-o, --source PATH` | required | YouTube link or path to an image or video |
| `-d, --destination DIRECTORY` | required | Output folder |
| `-f, --filename TEXT` | `ascii` | Output file name |
| `-s, --start INTEGER` | | Trim, start second |
| `-e, --end INTEGER` | | Trim, end second |
| `-r, --frame INTEGER` | | Render only the frame at this second as an image (`-s` and `-e` are ignored) |
| `-t, --threads INTEGER` | `8` | Threads for video processing, 1 to 32 |
| `-a, --chars TEXT` | `.;*uo` | ASCII characters from dark to light |
| `-p, --preset [720\|1080]` | | Settings that produce a 720p or 1080p file (`-h`, `-ft`, `-fs` and `-q` are ignored) |
| `-q, --sourcequality [360\|480\|720\|1080]` | `360` | Height the source is scaled down to. The result is about `fontsize/chunk` times this |
| `-h, --chunk INTEGER INTEGER` | `2 2` | Size of the pixel block that becomes one character, 0 to 128 |
| `-g, --gsv FLOAT FLOAT FLOAT` | `0.299 0.587 0.114` | RGB weights used when desaturating |
| `-c, --compression INTEGER` | `0` | PNG compression level, 0 to 9 |
| `-ft, --font FILE` | `moby.ttf` | Path to a custom font |
| `-fs, --fontsize INTEGER` | `6` | Font size, 0 to 128 |
| `-fc, --fontcolor INTEGER INTEGER INTEGER` | `255 255 255` | Font color |
| `--keepaspectratio` | off | Keep the original aspect ratio. Otherwise videos narrower than 16:9 get side bars |
| `--mute` | off | Drop the audio track |
| `--quiet` | off | Suppress console messages |
| `--help` | | Show the help and exit |

## License and credits

MIT License, see [LICENSE](LICENSE). The Moby font is bundled in `app/moby.ttf`.
