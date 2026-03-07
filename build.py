#!/usr/bin/env python
import sys
from pyappify.builder import Builder

if __name__ == '__main__':
    profile = sys.argv[1] if len(sys.argv) > 1 else 'Release'
    builder = Builder('pyappify.yml', profile)
    builder.build()
