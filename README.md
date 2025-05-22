# TLSv1.1_Scanner
A Python tool for scanning multiple hosts to detect TLSv1.1 support and track remediation progress.

# Features
Scan multiple hosts concurrently for TLSv1.1 support
Parse target lists with IP:PORT format
Two operation modes:
	Basic scan mode: Shows which hosts have TLSv1.1 enabled/disabled
        Remediation test mode: Tracks remediation status of hosts

# Requirements

Python 3.6+

sslscan command-line tool installed on your system

# Installation
   Clone this repository:

 ```
git clone https://github.com/yourusername/TLSv1.1_Scanner.git
cd TLSv1.1_Scanner
```
Make sure you have sslscan installed:
```
# On Debian/Ubuntu
sudo apt-get install sslscan

# On CentOS/RHEL
sudo yum install sslscan

# On macOS
brew install sslscan
```
# Usage
## Basic Scanning
To scan hosts and see which ones have TLSv1.1 enabled:	

```python tls10_check.py -i targets.txt```
	
## Remediation Testing
To check remediation status (shows REMEDIATED/NOT REMEDIATED for each host):	

```python tls10_check.py -i targets.txt -r```
	
## Command-line Options

```
-i, --input          Input file with targets (required)
-t, --threads        Number of concurrent threads (default: 10)
-r, --remediation_test  Run in remediation test mode
```

## Input File Format
Input File Format
The input file should contain one target per line in the following format:

```
192.168.1.1:443
example.com:8443
10.0.0.1
```

If no port is specified, the default port (443) will be used.
	
# Output Examples

```
# Here's a sample output for the script when scanning multiple hosts for TLSv1.1 support

[+] Loaded 8 targets from /home/user/targets.txt
[+] Scanning 192.168.1.10:443
[+] Scanning 192.168.1.11:443
[+] Scanning 192.168.1.12:443
[+] Scanning 192.168.1.13:443
[+] Scanning 192.168.1.14:443
[!] TLSv1.1 ENABLED on 192.168.1.11:443
[+] Scanning 192.168.1.15:443
[+] Scanning 192.168.1.16:443
[+] Scanning 192.168.1.17:443
[!] TLSv1.1 ENABLED on 192.168.1.15:443

[✓] Scan Results:

[!] Hosts with TLSv1.1 ENABLED:

    - 192.168.1.11:443
    - 192.168.1.15:443

[+] Hosts with TLSv1.1 DISABLED:

    - 192.168.1.10:443
    - 192.168.1.12:443
    - 192.168.1.13:443
    - 192.168.1.14:443
    - 192.168.1.16:443
    - 192.168.1.17:443
	
# And here's a sample output when running in remediation test mode (with the -r flag):

[+] Loaded 8 targets from /home/user/targets.txt
[+] Scanning 192.168.1.10:443
[+] Scanning 192.168.1.11:443
[+] Scanning 192.168.1.12:443
[+] Scanning 192.168.1.13:443
[+] Scanning 192.168.1.14:443
[!] TLSv1.1 ENABLED on 192.168.1.11:443
[+] Scanning 192.168.1.15:443
[+] Scanning 192.168.1.16:443
[+] Scanning 192.168.1.17:443
[!] TLSv1.1 ENABLED on 192.168.1.15:443

[✓] Remediation Test Results:

[!] Hosts with TLSv1.1 still ENABLED:

    192.168.1.11:443 - NOT REMEDIATED
    192.168.1.15:443 - NOT REMEDIATED

[+] Hosts with TLSv1.1 disabled:

    192.168.1.10:443 - REMEDIATED
    192.168.1.12:443 - REMEDIATED
    192.168.1.13:443 - REMEDIATED
    192.168.1.14:443 - REMEDIATED
    192.168.1.16:443 - REMEDIATED
    192.168.1.17:443 - REMEDIATED

[*] Total hosts scanned: 8
[*] Hosts with TLSv1.1 enabled: 2
[*] Hosts with TLSv1.1 disabled: 6

# If there's an error scanning a host, you might see something like:

[+] Scanning 192.168.1.18:443
[!] Error scanning 192.168.1.18:443: Command 'sslscan' returned non-zero exit status 1
[!] Warning: 1 hosts failed to scan properly
```

# License
MIT License

# Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
