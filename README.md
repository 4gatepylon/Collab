# What's This?
This is a hackathon project that aimed at creating a build/version-control system for Python scripts with Excel spreadhsheets. You have limited abilities to output from python into excel and input into python from excel (though only if it's outputting to another cell in excel). This also works over column ranges and sets of column ranges (shortest range is chosen and a mapping starting at the beginning of the range up to the distance of the smallest range's length up every range is used to pass in parameters to the function, which is assumed to take in singletons instead of slices/ranges).

Most of our work is in `.collab/` since we also intend(ed) to abstract away git functionality and provide a rudimentary GUI. In some eventuality we would have liked to have been able to put the entire repository somewhere like `~/.cache` (think bazel hidden files) and then symlinking into the desired folder. We'd ideally use a add-in to Excel, though a GUI would also be good. We have a basic GUI but it's quite inadequate.

The main contribution here is the code answer injection into excel, though there is also some unit testing for excel spreadsheets and the beginnings of version control support (abstracted away of course) plus pieces of GUI here and there that are a WIP.

This is very hacky and not particularly usable, but may prove to be a nice POC.

# What Would We Like To See?
1. Diffs of only dependencies
2. Diffs of only functions and also functions + dependencies
3. Diffs of only styling
4. Diffs of only constant data
5. Diffs of only code scripts
6. The ability to granularly revert (etc) seperately on these dimensions (i.e. multiplexing git)
7. Git abstracted away hidden in some folder (i.e. `~/.cache`) plus symlinks or some other way to access from your current dir
8. Add in to Excel or (slightly less convenient) am Electron App Gui
9. Onboarding to Git for non-technical users

# Hackathon Notes
## TODO
1. Get the CLI commands (particularly diff) to properly work with the hidden folder properly. Nicely encapsulate git so that we have some sort of onboarding flow where you run a script to set up your `.collab` and link to a git repository somewhere and then start editing excel spreadsheets.
2. Do a smart diff that is basically only non-hidden python files and some sort of tree object, maybe like a pydot or something in electron. Ignore the hidden files with `https://stackoverflow.com/questions/10415100/want-to-exclude-file-from-git-diff`.

## Top Existing Demoable Features
1. Function injection with callable name
2. Function injection with arguments, arguments that are ranges and range merging (multiple ranges)
3. Basic GUI to do "commits" and other version control functionality
4. Basic unit testing demo

## Collab
Excel + Git + Jupyter Notebook with Smart Diffing

On a high level this provides you a computational graph API for your project with Git. You can commit various diffent forms of source code (python, in the future potentially other languages like Java, C, and arbitrary build systems as long as they write to a tbd standardized format). Then it allows you to store everything in a Git repository that remembers the source code and Yaml. Then the yaml is generated into an Excel spreadsheet with the program outputs.

In the future we will add better GUIs to wrap git operations, potentially the option to output FROM Excel, and better onboarding flow. We also want to add better diffing UIs.

Current MVP is:
1. Parse and generate Excel from YAML file encoding a computation tree.
2. Insert dynamic data entries that expect output from Python files into the tree (turn into constant values in the generated excel).
3. When you change excel, translate parse the changes to the DOM and translate them into changes in the YAML. Only commit the YAML.

## Components
### Computation Graph
- Parse excel to Git
- Generate excel from Git
- Generate types for the Excel equations plus static and dynamic data (save some spots for dynamic data so we can support various input types; for example, you may want to generate rows and columns additionally to cells)

### Python
- Read Stdout from linked python files and add them to the Excel DOM

### Git
- Have the ability to commit from Excel on save (daemon) or as part of a Add-in
- Figure out diffing from Excel diff to YAML diff
- Wrappers for pulling/pushing

## Encoding Flow
1. Query user for commit information via GUI and store
2. Calculate excel diff
3. Detect source code diffs
4. Detect YAML diff from Excel Diff
5. Apply source code diffs to intermediate YAML
6. Apply excel diff (hard) to intermediate YAML
7. Write to the main YAML
8. Call git functionality

## Decoding Flow
1. Create a temporary XLSX file
2. Create a copy (intermediate YAML) of the YAML
3. Store list of dynamic data nodes and blank them out to be errors for now
4. Do a dag computation; for each node, if it is dynamic, compute linked python output and store it, replacing the errors and writing to the file; if it is static data then just write to the file; if it's a function then write the function to the file
5. Return the temporary file or error out

## YAML Structure
- List of Python files
- List of xslx files
- Links (i.e. declare a symbol for the output) between the python and xslx files (in YAML)
- For each xslx generate a sub-DAG with the symbols as nodes

## CLI Options
### Global
- Config (set any credentials you need to be able to do git operations)
### Repository
- Init (create a repository and optionally pull from a source)
- Stage (stage `*.py` files and changes to `*.xslx` files) (take in a regex to ignore certain files, or choose certain files)
- Commit (commits everything staged)
- Merge (combine two branches, error if you cannot: under the hood we'll rebase)
- Branch (create a new branch starting at the current commit)
- Push (try to push to origin, if it is ahead reject, if it's behind, rebase or fail)
- Pull (try to pull from origin and fast-forward and rebase, or fail)
- Reset (wind back time)
- Log (list of changes)
- Diff (show a meaningful diff)
### Linking
There is no linking command, they just need to add xlwings decorators. When we init, we will generate the boilerplate main in a hidden folder and then import in their files. Instead of them giving a location, they need to use the function.

## Help
To analyze an Exel file try running `unzip myfile.xslx`.