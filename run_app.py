#!/usr/bin/env python3
"""
Direct app launcher with embedded credentials
"""

import os
import sys

# Set Spotify credentials before any imports
os.environ['SPOTIFY_CLIENT_ID'] = 'd8d22be2095f480591ce7de628699e26'
os.environ['SPOTIFY_CLIENT_SECRET'] = '71fbff9545254217b40e800f222cba84'

# Now run the main application
if __name__ == "__main__":
    try:
        exec(open('main.py').read())
    except FileNotFoundError:
        print("Error: main.py not found in current directory")
        sys.exit(1)