Website-Ping-Scrambler V1

Scramble your ping requests for ISP Log Confusion.
Support my coding ventures — send donations to: https://cash.app/$SethKhaneki

Original Developer: https://github.com/BlackGTNinja a.k.a. (S3THCOD3R)

---

Overview

Website Ping Scrambler Pro is a network diagnostic tool that pings a large, diverse set of websites using ICMP, HTTP, or HTTPS requests. By rotating through hundreds of global, Japanese, and Russian sites at random, it produces traffic patterns that are harder for an ISP or network observer to categorize as simple "keepalive" or "monitoring" activity.

This is not a privacy/anonymity tool (no VPN, no Tor), but rather a traffic obfuscation utility designed to mix your outbound pings with legitimate lookups to major internet properties.

---

Features

· Three ping modes – ICMP (system ping), HTTP HEAD, HTTPS HEAD (with TLS handshake timing)
· Large site pool – 100 global + 100 Japanese + 100 Russian popular domains (no duplicates)
· Automatic failed site skipping – bans a site for N seconds after consecutive failures
· Live rolling statistics – success rate, latency average, TLS handshake time
· Per‑site performance tracking – fastest/slowest sites in the current window
· Interactive flag menu – change interval, timeout, workers, ban behavior while running
· Color-coded terminal output – clear visual feedback (auto‑disabled on non‑TTY)
· Cross‑platform – Windows, Linux, macOS (requires system ping command for ICMP mode)

---

Requirements

· Python 3.6+ (no external packages — uses only standard library)
· Internet connection (obviously)
· ping command available in system PATH (for ICMP mode only)

No pip install needed.

---

Installation & First Run

1. Save the script as website_scrambler.py
2. Make it executable (Linux/macOS):
   ```bash
   chmod +x website_scrambler.py
   ```
3. Run it:
   ```bash
   python3 website_scrambler.py
   ```

On first launch you will see an interactive mode selection menu:

```
[1]  ALL      — random mix of ICMP, HTTP, and HTTPS
[2]  HTTPS    — TLS handshake timing + cert inspection
[3]  HTTP     — plain HTTP HEAD requests
[4]  ICMP     — classic ping (uses system ping command)
```

After picking a mode, a flag configuration menu appears where you can adjust runtime options.

---

Command Line Arguments (Skip Interactive Menus)

Argument Description Default
--mode {icmp,http,https,all} Skip the mode selection menu (interactive)
--interval SEC Seconds between pings 1.0
--timeout SEC Per-request timeout 3.0
--workers N Concurrent ping workers (1‑64) 10
--skip-unreachable Enable automatic banning of failing sites enabled
--no-skip-unreachable Disable site banning –
--failure-threshold N Consecutive failures before ban 3
--ban-duration SEC How long a site stays banned 60.0

Examples

```bash
# HTTPS mode, faster interval, more workers
python3 website_scrambler.py --mode https --interval 0.5 --workers 20

# Disable skip logic, use ICMP only
python3 website_scrambler.py --mode icmp --no-skip-unreachable

# All modes, longer timeout, ban after 5 failures
python3 website_scrambler.py --mode all --timeout 5 --failure-threshold 5
```

If you provide --mode, the interactive mode menu is skipped. The flag configuration menu will still appear unless you also supply all other config arguments on the command line (the script always shows the flag menu once). You can press 7 (Done) immediately to continue without changes.

---

Output Explained

A typical live line looks like this:

```
[14:32:09] #42   HTTPS  ✓ 200     google.co.jp             45ms   tls 38ms   │ ✓41 ✗1 │ sr 97.6% avg 52ms
```

Field Meaning
[14:32:09] Current time
#42 Total pings issued so far
HTTPS Mode used (colors: magenta=HTTPS, blue=HTTP, cyan=ICMP)
✓ 200 HTTP status (200=OK) or REPLY for ICMP
google.co.jp Target site (truncated to 22 chars)
45ms Total request time
tls 38ms (HTTPS only) Time to complete TLS handshake
✓41 ✗1 Cumulative successes / failures
sr 97.6% avg 52ms Rolling success rate and average latency

Every 60 pings, a summary block is printed with statistics:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊  ROLLING STATS  (window 60, total 120)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  success rate : 96.7%   ✓ 116   ✗ 4
  latency (ms) : min 12   med 38   avg 41   max 187
  tls handshake: avg 34ms   min 22   max 89  (82 samples)
  by mode      : HTTPS 82/85 (96%)  ICMP 34/35 (97%)
```

At the end of the run (Ctrl+C), a final detailed summary shows fastest/slowest sites.

---

How "Site Skipping" Works

When --skip-unreachable is enabled (default):

1. Each site starts with a consecutive failure counter = 0.
2. If a request succeeds → counter resets to 0.
3. If a request fails → counter increments.
4. When counter reaches --failure-threshold (default 3), the site is banned for --ban-duration seconds.
5. Banned sites are excluded from the random selection pool.
6. After the ban expires, the site is re‑enabled and its failure counter resets.

This prevents the script from wasting time on dead or firewalled hosts.

---

Use Cases & Rationale

Scenario Why this helps
ISP noise generation Regular pings to random global sites make your traffic look like normal browsing / cloud monitoring, not a scheduled "heartbeat".
Network benchmarking Measure real‑world latency and TLS handshake times across hundreds of endpoints.
Firewall / censorship detection Compare ICMP vs HTTP vs HTTPS reachability to identify where blocks occur.
Learning tool See how TLS handshake latency differs from total HTTPS request time.

⚠️ This tool does not encrypt your traffic or hide your IP address. It only changes which hosts you ping and in what order, adding noise to simple traffic analysis.

---

Troubleshooting

ICMP mode fails on Linux/macOS

· Some systems require root for raw ICMP sockets. The script uses the system ping command, which works without root on most distributions. If you get ping: socket: Operation not permitted, try:
  ```bash
  sudo python3 website_scrambler.py --mode icmp
  ```

ssl.SSLCertVerificationError on HTTPS

· The script uses Python's default SSL context. If a site has an invalid certificate, it will be marked as a failure. This is intentional — invalid certs count as unreachable.

High latency / timeouts

· Reduce --workers (e.g., 5) and increase --timeout (e.g., 5). The script may overwhelm a slow connection.

Windows: 'ping' is not recognized

· Ensure ping.exe is in your PATH (it normally is). If not, reinstall Windows’ built-in networking tools.

Terminal colors not showing

· Colors are automatically disabled when output is redirected to a file or pipe. Force colors with FORCE_COLOR=1 python3 script.py.

---

License & Disclaimer

This script is provided as is for educational and network diagnostic purposes. Misuse against networks you do not own or have permission to test may violate laws or terms of service. The developer assumes no liability.

---

Enjoy scrambling.
— Seth Khaneki (S3THCOD3R)