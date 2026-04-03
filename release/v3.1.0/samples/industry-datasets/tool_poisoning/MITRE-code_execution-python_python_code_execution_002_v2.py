#!/usr/bin/env python3

"""Code execution - code_execution"""
import os
import sys

# Remote code execution
code = input("Enter code: ")
exec(code)

# Command injection
cmd = "ls -la " + sys.argv[1]
os.system(cmd)
