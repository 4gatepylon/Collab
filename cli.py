import click

@click.group()
def cli():
   pass

@click.command()
def pull():
    click.echo('Hello there')

@click.command()
def push():
    click.echo('Hello there')

@click.command()
def commit():
    click.echo('Hello there')

@click.command()
def diff():
    click.echo('Hello there')


if __name__ == '__main__':
   cli.add_command(pull)
   cli.add_command(push)
   cli.add_command(diff)
   cli.add_command(commit)

   cli()
