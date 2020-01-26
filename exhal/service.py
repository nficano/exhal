import click
from breathe import Breathe
from daemon import Daemon


class Service(Daemon):
    def __init__(self):
        self.cls = super().__init__()
        self.breathe = Breathe()

    def run(self):
        self.breathe.start()

    def shutdown(self):
        self.breathe.stop()
        self.cls.stop()


service = Service()


@click.group()
def cli():
    pass


@cli.command()
def stop():
    service.stop()


@cli.command()
def start():
    service.start()


@cli.command()
def restart():
    service.restart()


if __name__ == "__main__":
    cli()
