import click
from app.asciiclip import ASCIIClip


@click.group()
def cli():
    pass


@cli.command(name='mvgen')
@click.option('-u', '--url', type=str)
@click.option('-d', '--destination', type=click.Path(exists=True))
def mvgen(url, destination):
    ASCIIClip().generate_video(url, destination)


@cli.command(name='imgen')
@click.option('-u', '--url', type=str)
@click.option('-d', '--destination', type=click.Path(exists=True))
def imgen(url, destination):
    ASCIIClip().generate_image(url, destination)


if __name__ == '__main__':
    cli()
