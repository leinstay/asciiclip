import click
from lib.asciiclip import ASCIIClip


@click.group()
def cli():
    pass


@cli.command()
def mvgen(url, destination):
    ASCIIClip().generate_video(None, None)


@cli.command()
def imgen(url, destination):
    ASCIIClip().generate_image(None, None)


if __name__ == '__main__':
    cli()
