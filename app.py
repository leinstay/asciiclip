import click
from asciiclip import ASCIIClip


@click.group()
def cli():
    pass


@cli.command()
def mvgen():
    ASCIIClip().generate_video(None, None)


@cli.command()
def imgen():
    ASCIIClip().generate_image(None, None)


if __name__ == '__main__':
    cli()
