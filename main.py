import click
from app.asciiclip import ASCIIClip
from multiprocessing import cpu_count


@click.command(no_args_is_help=True)
@click.option('-o', '--source', type=click.Path(), help='Link to YouTube video or path to image or video', required=True)
@click.option('-d', '--destination', type=click.Path(file_okay=False, writable=True, resolve_path=True), help='Output folder', required=True)
@click.option('-f', '--filename', type=str, help='Output file name', required=False, default='ascii', show_default=True)
@click.option('-s', '--start', type=int, help='Used to trim video, sets the beginning point in seconds', required=False, default=None, show_default=True)
@click.option('-e', '--end', type=int, help='Used to trim video, sets the ending point in seconds', required=False, default=None, show_default=True)
@click.option('-r', '--frame', type=int, help='Turns the frame at a specified second of video into an image (-s/-e will be ignored)', required=False, default=None, show_default=True)
@click.option('-t', '--threads', type=click.IntRange(1, 32), help='Number of threads used for video processing', required=False, default=cpu_count(), show_default=True)
@click.option('-a', '--chars', type=str, help='List of ASCII characters arranged from dark to light', required=False, default=".;*uo", show_default=True)
@click.option('-p', '--preset', type=click.Choice(['720', '1080']), help='A set of settings that will produce a 720p or 1080p output file (-h/-ft/-fs/-q will be ignored)', required=False)
@click.option('-q', '--sourcequality', type=click.Choice(['360', '480', '720', '1080']), help='Height in pixels to which the video or image will be scaled down (the final result will be about [fontsize/chunk] times this value)', required=False, default='360', show_default=True)
@click.option('-h', '--chunk', type=click.IntRange(0, 128), nargs=2, help='Size of the rectangular area that will be consolidated to a single ASCII symbol', required=False, default=(2, 2), show_default=True)
@click.option('-g', '--gsv', type=click.FloatRange(0, 1), nargs=3, help='RGB weights used when desaturating an image or video', required=False, default=(0.299, 0.587, 0.114), show_default=True)
@click.option('-c', '--compression', type=click.IntRange(0, 9), help='PNG compression level', required=False, default=0, show_default=True)
@click.option('-ft', '--font', type=click.Path(exists=True, dir_okay=False, resolve_path=True), help='Path to custom font', required=False, default=ASCIIClip.default_font, show_default=True)
@click.option('-fs', '--fontsize', type=click.IntRange(0, 128), help='Font size', required=False, default=6, show_default=True)
@click.option('-fc', '--fontcolor', type=click.IntRange(0, 255), nargs=3, help='Font color', required=False, default=(255, 255, 255), show_default=True)
@click.option('--keepaspectratio', is_flag=True, help='Preserves original aspect ratio, otherwise if the video is thinner than 16:9 bars will be added to the sides', required=False)
@click.option('--mute', is_flag=True, help='Removes the audio track from the video', required=False)
@click.option('--quiet', is_flag=True, help='Suppress all console messages', required=False)
def generate(chunk, chars, gsv, compression, sourcequality, preset, fontsize, fontcolor, font, source,
             destination, filename, start, end, frame, threads, quiet, keepaspectratio, mute):
    """
    CLI tool that applies an ASCII filter to video or image
    """
    _ = ASCIIClip(chunk, tuple(list(chars)), list(gsv), compression, not keepaspectratio,
                  sourcequality, preset, not quiet, fontsize, fontcolor, font)
    _.generate(source, destination, filename,
               (start, end) if frame is None else frame, threads, mute)


if __name__ == '__main__':
    generate()
