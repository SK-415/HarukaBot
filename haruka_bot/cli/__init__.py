import click

from .utils import create_env


@click.group()
def main():
    pass


@click.command()
def run():
    create_env()
    from .bot import run

    run()


main.add_command(run)
