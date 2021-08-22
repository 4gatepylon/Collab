import click

import subprocess
from glob import glob
from subprocess import Popen, PIPE
from serialization import serialize
import sys
import os

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
@click.option("--message", default="Commit", help="Commit message")
def commit(message):
    excel_filenames = all('.xlsx')
    yaml_path = os.path.basename(excel_filenames[0]) if len(excel_filenames) else 'master.yaml'
    serialize(filenames=excel_filenames, yaml_path=yaml_path)
    subprocess.call(["git", "add", "."])
    subprocess.call(["git", "commit", "-m", message])

# all files in all subdirectories as well as this directory
def all(ext):
    return glob("**/*." + ext) + glob("*." + ext)

# hii
@click.command()
def diff():
    with Popen(
        ["git", "diff", "--minimal", "--color"] +
        all("yml") + 
        all("yaml") +
        all("py"), stdout=PIPE) as p:
        Popen(["cat"], stdin=p.stdout).wait()
        p.stdout.close()

@click.command()
def exitProgram():
    sys.exit()



if __name__ == '__main__':
   cli.add_command(pull)
   cli.add_command(push)
   cli.add_command(diff)
   cli.add_command(commit)
   cli.add_command(init)

   cli()
