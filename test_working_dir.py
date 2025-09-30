#!/usr/bin/env python3

import os
import sys

print("=== Working Directory Test ===")
print(f"Command line args: {sys.argv}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
print(f"User home directory: {os.path.expanduser('~')}")
print(f"Python executable: {sys.executable}")

# Test cache path determination
home_dir = os.path.expanduser('~')
glping_home = os.path.join(home_dir, 'glping')
cache_path = os.path.join(glping_home, 'cache.json')

print(f"Expected cache path: {cache_path}")
print(f"Cache path exists: {os.path.exists(cache_path)}")

if os.path.exists(cache_path):
    print(f"Cache file permissions: {oct(os.stat(cache_path).st_mode)[-3:]}")
    print(f"Cache file owner: {os.stat(cache_path).st_uid}")