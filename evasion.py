#!/usr/bin/env python3
"""
evasion.py — HiddenBytes Evasion Program
Educational tool for understanding binary obfuscation and AV evasion techniques.
"""

import argparse
import os
import sys
import time
import struct
import random
import hashlib
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
log = logging.getLogger("evasion")