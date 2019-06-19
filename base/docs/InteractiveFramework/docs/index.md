# Welcome to the Interactive Framework

## Summary
The Interactive Framework was created to modulate existing scripts into a single toolset.<br>
The Framework will dynamically import modules from the module directory, provide recommendations on
commands, and allow you to run a module interactively or run with the necessary arguments from the main menu.<br>

Alternatively, a flag is added to the `aem_util.py` script so you can run your module and arguments in a single command.
This is useful when designing jenkins jobs or other scheduled automation tasks.

## Project layout
- `aem_util.py` <sub>_(Script Calls the actual framework with an easy to use name)_ </sub><br>
- **base/** <br>
    - `main.py` <sub>_(Main script for Interactive Framework)_</sub><br>

    - **core/**   <sub>_(Directory for Core Framework Modules)_</sub><br>
        - `get_arguments.py`  <sub>_(Module That Defines arguments for main.py)_</sub><br>
        - `pyCommon.py`  <sub>_(Module That Defines common imports and variables for import)_</sub><br>

    - **modules/**  <sub>_(Directory to store Modules)_</sub><br>
        - `encode_password.py`  <sub>_(Module to encode / decode passwords)_</sub><br>
        - `sql_query.py` <sub>_(Module to perform SQLite3 queries and return results)_</sub><br>
        - `<Your Custom Module Here>`

## How to Run
To Run, simply run python and the `aem_util.py` like so:<br>
`python /path/to/aem_util.py` <br>

To execute in a single command and avoid running the main menu, Simply use the -m argument.<br>
This example runs the `sql_query.py` module with multiple arguments
Example: `python3 aem_util.py -m "encode_password --encode test"`

###Main Menu + recommendations:
![Main Menu](./images/main_menu.png)

###Dynamically Import Modules without changing code:
![Show Modules Command](./images/show_modules.png)

###Run Module Interactive:
![Interactive1](./images/interactive1.png) <br><br>
![Interactive2](./images/interactive2.png)

###Module Help / Acceptable Arguments:
![Help](./images/help.png)

###Execute Module With Acceptable Arguments:
![Run with Arguments](./images/run_with_args.png)

###Exit Module:
![Exit](./images/exit.png)


