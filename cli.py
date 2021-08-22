import click

import subprocess
from subprocess import Popen, PIPE

@click.group()
def cli():
   pass

@click.command()
def pull():
    subprocess.call(["git", "pull"])

# Assume they have SSH setup with their github or somehow have access to the github repository
@click.command()
@click.option("--remote", default=None, help="Git Source")
def init(remote):
    if remote is None:
        subprocess.call(["git", "init"])
    else:
        # TODO copy into a hidden folder somewhere instead
        subprocess.call(["git", "clone", remote])

@click.command()
def push():
    subprocess.call(["git", "push"])

@click.command()
@click.option("--message", default="No message", help="Commit message")
def commit(message):
    subprocess.call(["git", "add", "."])
    subprocess.call("git", "commit", "-m", message)

@click.command()
def diff():
    with Popen(["git", "diff", "--minimal", "--color"], stdout=PIPE) as p:
        Popen(["cat"], stdin=p.stdout).wait()
        p.stdout.close()



if __name__ == '__main__':
   cli.add_command(pull)
   cli.add_command(push)
   cli.add_command(diff)
   cli.add_command(commit)
   cli.add_command(init)

   cli()
