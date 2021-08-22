# Collab
Excel + Git + Jupyter Notebook with Smart Diffing

On a high level this provides you a computational graph API for your project with Git. You can commit various diffent forms of source code (python, in the future potentially other languages like Java, C, and arbitrary build systems as long as they write to a tbd standardized format). Then it allows you to store everything in a Git repository that remembers the source code and Yaml. Then the yaml is generated into an Excel spreadsheet with the program outputs.

In the future we will add better GUIs to wrap git operations, potentially the option to output FROM Excel, and better onboarding flow. We also want to add better diffing UIs.

Current MVP is:
1. Parse and generate Excel from YAML file encoding a computation tree.
2. Insert dynamic data entries that expect output from Python files into the tree (turn into constant values in the generated excel).
3. When you change excel, translate parse the changes to the DOM and translate them into changes in the YAML. Only commit the YAML.

# Components
## Computation Graph
- Parse excel to Git
- Generate excel from Git
- Generate types for the Excel equations plus static and dynamic data (save some spots for dynamic data so we can support various input types; for example, you may want to generate rows and columns additionally to cells)

## Python
- Read Stdout from linked python files and add them to the Excel DOM

## Git
- Have the ability to commit from Excel on save (daemon) or as part of a Add-in
- Figure out diffing from Excel diff to YAML diff
- Wrappers for pulling/pushing

# Encoding Flow
1. Query user for commit information via GUI and store
2. Calculate excel diff
3. Detect source code diffs
4. Detect YAML diff from Excel Diff
5. Apply source code diffs to intermediate YAML
6. Apply excel diff (hard) to intermediate YAML
7. Write to the main YAML
8. Call git functionality

# Decoding Flow
1. Create a temporary XLSX file
2. Create a copy (intermediate YAML) of the YAML
3. Store list of dynamic data nodes and blank them out to be errors for now
4. Do a dag computation; for each node, if it is dynamic, compute linked python output and store it, replacing the errors and writing to the file; if it is static data then just write to the file; if it's a function then write the function to the file
5. Return the temporary file or error out

# YAML Structure
- List of Python files
- List of xslx files
- Links (i.e. declare a symbol for the output) between the python and xslx files (in YAML)
- For each xslx generate a sub-DAG with the symbols as nodes

# CLI Options
## Global
- Config (set any credentials you need to be able to do git operations)
## Repository
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
## Linking
There is no linking command, they just need to add xlwings decorators. When we init, we will generate the boilerplate main in a hidden folder and then import in their files. Instead of them giving a location, they need to use the function.

# Help
To analyze an Exel file try running `unzip myfile.xslx`.