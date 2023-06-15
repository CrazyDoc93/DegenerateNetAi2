import importlib
import inspect
import os
from pathlib import Path
from typing import *


class Module:
    def __init__(self, name: str, path: Union[Path, str], run):
        self.name = name
        self.path = path
        self.instance = run


class Modules:
    def __init__(self, path: str) -> None:
        self.path = path
        self.modules: List[Module] = []

    def load_modules(self) -> None:
        """
        Loads all the modules in the specified path
        """
        for file in os.listdir(self.path):
            if file.endswith(".py") and not file.startswith("__"):
                self.load_function(file[:-3], os.path.join(self.path, file))

    def load_function(self, name: str, path: str):
        """
        Loads a python function from a file and registers it as a function in the current session

        :param name: The name of the function
        :type name: str
        :param path: The path to the file that contains the function
        :type path: str
        """
        spec = importlib.util.spec_from_file_location(name, path)
        function = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(function)

        self.register_function(function, path)

    def register_function(self, module, path):
        """
        It imports all the functions from the module and adds them to the list of functions.

        :param module: The module that contains the functions you want to register
        """
        for classname, classobj in inspect.getmembers(module, inspect.isclass):
            if classname.endswith("Func") and classname != "BaseFunc":
                self.modules.append(
                    Module(
                        name=classobj.__doc__,
                        path=Path(path),
                        run=classobj,
                    )
                )
