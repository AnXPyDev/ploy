#!/usr/bin/python

import xml.etree.ElementTree as XML
from argparse import ArgumentParser
import re
from copy import deepcopy

# util

def normdir(path):
    if path != "/":
        path += "/"
    return path

def filedir(path):
    splits = path.split("/")
    splits[-1] = splits[-1].split(".")[0]
    return splits.join("/") + "/"

def parentdir(path):
    splits = path.split("/")
    splits.pop()
    return splits.join("/") + "/"


# types

class TypeStore:
    def __init__(self):
        self.store = {}

    def get(self, name):
        return self.store.get(name, None)

    def set(self, name, type_val):
        self.store[name] = type_val

class FileStore:
    def __init__(self):
        self.dependencies = {}
        self.files = {}

    def addDependency(self, path, dependency):
        if path in self.dependencies:
            return
        self.dependencies[path] = dependency

    def addFile(self, path, file):
        if path in self.files:
            return
        self.files[path] = file

class Dependency:
    def __init__(self, path):
        self.path = path

class RegexDependency:
    def __init__(self, regex):
        self.regex = regex

    def getDeps(self, file_content):
        result = []

class Type:
    def __init__(self, node=None):
        self.compiler = None
        self.files = None
        self.glob = None
        self.include_directories = []
        self.dependencies = []

    def extend(self, other):
        if self.compiler == None: self.compiler = deepcopy(other.compiler)
        if self.files == None: self.files = deepcopy(other.files)
        if self.glob == None: self.glob = deepcopy(other.glob)

        self.include_directories.extend(deepcopy(other.include_directories))
        self.dependencies.extend(deepcopy(other.dependencies))

class Argument:
    def __init__(self, node=None):
        self.position = None
        self.priority = None
        if node != None:
            position = node.attrib.get("position")
            if position == None:
                self.position = 50;
            elif position == "before":
                self.position = 25
            elif position == "middle":
                self.position = 50
            elif position == "after":
                self.position = 75
            else:
                self.position = int(position)

            priority = node.attrib.get("priority")
            if priority == None:
                self.priority = 50
            if priority == "first":
                self.priority = 25
            elif priority == "last":
                self.priority = 75
            else:
                self.priority = int(priority)

    def getValue(self, file):
        return None
    
    def __str__(self):
        return f"Argument \{ position: {self.positon}, priority: {self.priority} \}"
    

class ConstantArgument(Argument):
    def __init__(self, node = None):
        super().__init__(node)

        self.value = None
        if node != None:
            value = node.attrib.get("value")
            if value == None: value = node.text
            self.value = value

    def getValue(self, file):
        return self.value

    def __str__(self):
        return f"ConstantArgument {{ position: {self.position}, priority: {self.priority}, value: {self.value} }}"
   

class CompileTimeArgument(Argument):
    def __init__(self, node = None):
        super().__init__(node)
        self.value = None
        self.before = ""
        self.after = ""
        self.function = None
        if node != None:
            self.function = node.tag
            self.before = node.attrib.get("before", "")
            self.after = node.attrib.get("after", "")

    def getValue(self, file):
        value = "error"
        return self.before + value + self.after

    def __str__(self):
        return f"CompileTimeArgument {{ position: {self.position}, priority: {self.priority}, function: {self.function}, before: {self.before}, after: {self.after} }}"

    
def parse_compiler_arg(node):
    if node.tag == "argument":
        return ConstantArgument(node)
    else:
        return CompileTimeArgument(node)

class Compiler:
    def __init__(self, node=None):
        self.executable = None
        self.arguments = []
        if node != None:
            for prop in node:
                if prop.tag == "executable":
                    self.executable = prop.attrib.get("path")
                    continue

                self.arguments.append(parse_compiler_arg(prop))


class Source:
    def __init__(self, node=None):
        self.input_path = None
        self.output_path = None


# globals

store = TypeStore()
store.set("default", Type())
default_type = store.get("default")

input_directory = "./"
output_directory = "./"
include_directories = []

# parser

def parse_sources(node):
    print(node.tag)

def parse_types(node):
    print(node.tag)

def parse_config(node):
    global input_directory, output_directory, include_directories
    for prop in node:
        if prop.tag == "input-directory":
            input_directory = normdir(prop.attrib.get("path", prop.text))
        elif prop.tag == "output-directory":
            output_directory = normdir(prop.attrib.get("path", prop.text))
        elif prop.tag == "include-directory":
            path = normdir(prop.attrib.get("path", prop.text))
            if not path in include_directories:
                include_directories.append(path)
        elif prop.tag == "relative-include-directory":
            path = input_directory + normdir(prop.attrib.get("path", prop.text))
            if not path in include_directories:
                include_directories.append(path)
        elif prop.tag == "compiler":
            default_type.compiler = Compiler(prop)
            for i in default_type.compiler.arguments:
                print(i)


def parse_recipe(path):
    tree = XML.parse(path)
    root = tree.getroot()

    for node in root:
        if node.tag == "config":
            parse_config(node)
        elif node.tag == "types":
            parse_types(node)
        elif node.tag == "sources":
            parse_sources(sources)

def main():
    parser = ArgumentParser(description="Generate Makefiles from xml description of project")
    parser.add_argument("recipe_file", metavar="RECIPE", help="path to xml recipe file", nargs="?", default="recipe.xml")

    args = parser.parse_args()

    parse_recipe(args.recipe_file)

if __name__ == "__main__":
    main()
