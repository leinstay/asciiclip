import click
from app.asciiclip import ASCIIClip


@click.group()
def cli():
    pass


@cli.command(name='mvgen')
@click.argument('-u', '--url', help='url', type=str)
@click.argument('-d', '--destination', help='destination', type=click.Path(exists=True))
def mvgen(url, destination):
    ASCIIClip().generate_video(url, destination)


@cli.command(name='imgen')
@click.argument('-u', '--url', help='url', type=str)
@click.argument('-d', '--destination', help='destination', type=click.Path(exists=True))
def imgen(url, destination):
    ASCIIClip().generate_image(url, destination)


if __name__ == '__main__':
    cli()
