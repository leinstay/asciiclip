import click
from app.asciiclip import ASCIIClip
from multiprocessing import cpu_count


@click.group()
def cli():
    pass


@cli.command()
@click.option('-o', '--source', type=click.Path(), help='TODO', required=True)
@click.option('-d', '--destination', type=click.Path(file_okay=False, writable=True, resolve_path=True), help='TODO', required=True)
@click.option('-s', '--start', type=int, help='TODO', required=False, default=None, show_default=True)
@click.option('-e', '--end', type=int, help='TODO', required=False, default=None, show_default=True)
@click.option('-f', '--filename', type=str, help='TODO', required=False, default='ascii', show_default=True)
@click.option('-t', '--threads', type=click.IntRange(1, 32), help='TODO', required=False, default=cpu_count(), show_default=True)
@click.option('-a', '--chars', type=str, help='TODO', required=False, default=".;*uo", show_default=True)
@click.option('-c', '--chunk', type=click.IntRange(0, 128), nargs=2, help='TODO', required=False, default=(2, 2), show_default=True)
@click.option('-g', '--gsv', type=click.FloatRange(0, 1), nargs=3, help='TODO', required=False, default=(0.299, 0.587, 0.114), show_default=True)
@click.option('-c', '--compression', type=click.IntRange(0, 9), help='TODO', required=False, default=0, show_default=True)
@click.option('-q', '--sourcequality', type=click.Choice(['360', '480', '720', '1080']), help='TODO', required=False, default='360', show_default=True)
@click.option('-p', '--preset', type=click.Choice(['720', '1080']), help='TODO', required=False, default='1080', show_default=True)
@click.option('-ft', '--font', type=click.Path(exists=True, dir_okay=False, resolve_path=True), help='TODO', required=False, default=ASCIIClip.defaultfont, show_default=True)
@click.option('-fs', '--fontsize', type=click.IntRange(0, 128), help='TODO', required=False, default=6, show_default=True)
@click.option('-fc', '--fontcolor', type=click.IntRange(0, 255), nargs=3, help='TODO', required=False, default=(255, 255, 255), show_default=True)
@click.option('--keepaspectratio', is_flag=True, help='TODO', required=False)
@click.option('--quiet', is_flag=True, help='TODO', required=False)
def mvgen(chunk, chars, gsv, compression, sourcequality, preset, fontsize, fontcolor, font, source,
          destination, filename, start, end, threads, quiet, keepaspectratio):
    _ = ASCIIClip(chunk, tuple(list(chars)), list(gsv), compression, not keepaspectratio,
                  sourcequality, preset, fontsize, fontcolor, font)
    _.generate_video(source, destination, filename, (start, end),
                     threads, not quiet, not quiet)


if __name__ == '__main__':
    cli()
