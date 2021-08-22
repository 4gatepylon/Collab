import click
import sys

@click.group()
def cli():
   print('hello')

@click.command()
def pull():
   print('hello')

@click.command()
def init():
   print('hello')

@click.command()
def push():
   print('hello')

@click.command()
def commit():
   print('hello')

@click.command()
def diff():
   print('hello')

@click.command()
def exitProgram():
   sys.exit()

if __name__ == '__main__':
   cli.add_command(push)
   cli.add_command(diff)
   cli.add_command(commit)
   cli.add_command(init)

   cli()
