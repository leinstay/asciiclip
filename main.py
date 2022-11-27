import click
from app.asciiclip import ASCIIClip
from multiprocessing import cpu_count


@click.group()
def cli():
    pass


@cli.command()
@click.option('-u', '--url', type=str, help='TODO', required=True)
@click.option('-d', '--destination', type=click.Path(file_okay=False, writable=True, resolve_path=True), help='TODO', required=True)
@click.option('-f', '--filename', type=str, help='TODO', required=False, default='ascii', show_default=True)
@click.option('-s', '--start', type=int, help='TODO', required=False, default=None, show_default=True)
@click.option('-e', '--end', type=int, help='TODO', required=False, default=None, show_default=True)
@click.option('-t', '--threads', type=int, help='TODO', required=False, default=cpu_count(), show_default=True)
@click.option('-a', '--chars', type=str, help='TODO', required=False, default=".;*uo", show_default=True)
@click.option('-c', '--chunk', type=int, nargs=2, help='TODO', required=False, default=(2, 2), show_default=True)
@click.option('-g', '--gsv', type=float, nargs=3, help='TODO', required=False, default=(0.299, 0.587, 0.114), show_default=True)
@click.option('-c', '--compression', type=int, help='TODO', required=False, default=0, show_default=True)
@click.option('-q', '--sourcequality', type=str, help='TODO', required=False, default="360p", show_default=True)
@click.option('-p', '--preset', type=str, help='TODO', required=False, default="1080p", show_default=True)
@click.option('-ft', '--font', type=str, help='TODO', required=False, default=ASCIIClip.defaultfont, show_default=True)
@click.option('-fs', '--fontsize', type=int, help='TODO', required=False, default=6, show_default=True)
@click.option('-fc', '--fontcolor', type=int, nargs=3, help='TODO', required=False, default=(255, 255, 255), show_default=True)
@click.option('--keepaspectratio', is_flag=True, help='TODO', required=False)
@click.option('--quiet', is_flag=True, help='TODO', required=False)
def mvgen(chunk, chars, gsv, compression, sourcequality, preset, fontsize, fontcolor, font, url,
          destination, filename, start, end, threads, quiet, keepaspectratio):

    _ = ASCIIClip(chunk, tuple(list(chars)), list(gsv), compression, not keepaspectratio,
                  sourcequality, preset, fontsize, fontcolor, font)
    _.generate_video(url, destination, filename, (start, end),
                     threads, not quiet, not quiet)


if __name__ == '__main__':
    cli()
