#!/usr/bin/env python3
"""
Website Ping Scrambler Pro by Seth Khaneki's - Azazel — ICMP + HTTP + HTTPS edition.
Now with automatic skipping of unreachable sites (configurable) and interactive flag menu.
Includes 100 Global + 100 Japanese + 100 Russian popular sites.
"""

import argparse
import os
import platform
import random
import re
import signal
import socket
import ssl
import statistics
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# ────────────────────────────  DEFAULTS  ─────────────────────────────────
DEFAULT_INTERVAL   = 1.0
DEFAULT_TIMEOUT    = 3.0
DEFAULT_WORKERS    = 10
ROLLING_WINDOW     = 60
SUMMARY_EVERY      = 60

# ───────────────────────────  ANSI COLORS  ────────────────────────────────
USE_COLOR = sys.stdout.isatty() or os.environ.get("FORCE_COLOR") == "1"
def c(code): return code if USE_COLOR else ""
RESET, BOLD, DIM     = c("\033[0m"), c("\033[1m"), c("\033[2m")
GREEN, YELLOW, RED   = c("\033[32m"), c("\033[33m"), c("\033[31m")
CYAN, MAGENTA, BLUE  = c("\033[36m"), c("\033[35m"), c("\033[34m")
GREY                 = c("\033[90m")

# ───────────────────────  SITE LISTS (Global + Japanese + Russian) ─────────
# 100 global popular sites
GLOBAL_SITES = [
    "google.com","youtube.com","facebook.com","amazon.com","twitter.com",
    "wikipedia.org","reddit.com","netflix.com","instagram.com","linkedin.com",
    "apple.com","microsoft.com","yahoo.com","imgur.com","x.com",
    "tiktok.com","discord.com","twitch.tv","pinterest.com","tumblr.com",
    "spotify.com","adobe.com","zoom.us","whatsapp.com","telegram.org",
    "medium.com","github.com","stackoverflow.com","quora.com","paypal.com",
    "ebay.com","etsy.com","walmart.com","target.com","bestbuy.com",
    "cnn.com","bbc.com","nytimes.com","washingtonpost.com","reuters.com",
    "theguardian.com","foxnews.com","nbcnews.com","bloomberg.com","forbes.com",
    "alibaba.com","aliexpress.com","shopify.com","cloudflare.com","aws.amazon.com",
    "cloud.google.com","azure.microsoft.com","digitalocean.com","vultr.com","linode.com",
    "salesforce.com","oracle.com","sap.com","ibm.com","intel.com",
    "amd.com","nvidia.com","samsung.com","huawei.com","xiaomi.com",
    "opera.com","brave.com","mozilla.org","duckduckgo.com","bing.com",
    "yahoo.co.jp","baidu.com","yandex.ru","naver.com","daum.net",
    "weibo.com","taobao.com","jd.com","tencent.com","bilibili.com",
    "booking.com","tripadvisor.com","airbnb.com","uber.com","lyft.com",
    "doordash.com","grubhub.com","postmates.com","instacart.com","robinhood.com",
    "coinbase.com","binance.com","kraken.com","patreon.com","substack.com",
    "notion.so","trello.com","asana.com","monday.com","slack.com",
    "docs.google.com","drive.google.com","mail.google.com","maps.google.com","play.google.com",
]

# 100 popular Japanese sites
JAPANESE_SITES = [
    "google.co.jp","yahoo.co.jp","amazon.co.jp","rakuten.co.jp","dmm.com",
    "nicovideo.jp","fc2.com","livedoor.com","goo.ne.jp","nifty.com",
    "hatena.ne.jp","ameblo.jp","line.me","yahoo.co.jp","mercari.com",
    "paypay.ne.jp","zozo.jp","yodobashi.com","biccamera.com","kakaku.com",
    "price.com", "tabelog.com","retty.me","gurunavi.com","hotpepper.jp",
    "weathernews.jp","tenki.jp","diamond.jp","toyokeizai.net","nikkei.com",
    "asahi.com","yomiuri.co.jp","mainichi.jp","sankei.com","japantimes.co.jp",
    "nhk.or.jp","fnn.jp","tbs.co.jp","fujitv.co.jp","tv-asahi.co.jp",
    "famitsu.com","4gamer.net","dengekionline.com","automaton-media.com","inside-games.jp",
    "pixiv.net","niconico.com","tumblr.com","note.com","coconala.com",
    "skima.jp","crowdworks.jp","lance.com","wantedly.com","green-japan.com",
    "jreast.co.jp","jr-central.co.jp","jr-west.co.jp","ana.co.jp","jal.co.jp",
    "odakyu.jp","keio.co.jp","tokyu.co.jp","seiburailway.jp","hankyu.co.jp",
    "nintendo.co.jp","sony.co.jp","toyota.co.jp","honda.co.jp","canon.co.jp",
    "panasonic.co.jp","sharp.co.jp","toshiba.co.jp","fujitsu.com","nec.com",
    "docomo.ne.jp","au.com","softbank.jp","rakuten-mobile.jp","ymobile.jp",
    "mu-mo.net","oricon.co.jp","billboard-japan.com","natalie.mu","barks.jp",
    "jp.sputniknews.com","japan-forward.com","savvytokyo.com","tokyoweekender.com","matcha-jp.com",
    "gov-online.go.jp","kantei.go.jp","meti.go.jp","moj.go.jp","mofa.go.jp",
    "mext.go.jp","mod.go.jp","mlit.go.jp","env.go.jp","cao.go.jp",
]

# 100 popular Russian sites
RUSSIAN_SITES = [
    "yandex.ru","mail.ru","vk.com","ok.ru","rambler.ru",
    "avito.ru","ozon.ru","wildberries.ru","lamoda.ru","sberbank.ru",
    "tinkoff.ru","alfabank.ru","gazprombank.ru","vtb.ru","rshb.ru",
    "kinopoisk.ru","ivi.ru","rutube.ru","sputnik.ru","lenta.ru",
    "ria.ru","tass.ru","rbc.ru","kommersant.ru","vedomosti.ru",
    "fontanka.ru","e1.ru","ngs.ru","nn.ru","74.ru",
    "163.com","yandex.com","cian.ru","domofond.ru","realty.yandex.ru",
    "auto.ru","avto.ru","drive2.ru","drom.ru","zr.ru",
    "pikabu.ru","fishki.net","yaplakal.com","bash.im","joyreactor.cc",
    "rutracker.org","nnmclub.to","kinozal.tv","hdrezka.ag","lostfilm.tv",
    "mos.ru","spb.ru","krskstate.ru","nso.ru","kuban.ru",
    "mcdonalds.ru","kfc.ru","burgerking.ru","subway.ru","starbucks.ru",
    "eldorado.ru","mvideo.ru","citilink.ru","dns-shop.ru","technopoint.ru",
    "ozon.ru","sima-land.ru","beru.ru","goods.ru","apteka.ru",
    "gb.ru","skillbox.ru","netology.ru","geekbrains.ru","stepik.org",
    "codecademy.com","habr.com","tproger.ru","proglib.io","python.org",
    "mts.ru","beeline.ru","megafon.ru","tele2.ru","tinkoff.mobile",
    "rkn.gov.ru","nalog.ru","gosuslugi.ru","rosreestr.ru","pfrf.ru",
    "cbr.ru","minfin.ru","economy.gov.ru","digital.gov.ru","minpromtorg.gov.ru",
]

# Combine all sites (remove duplicates while preserving order)
WEBSITES = []
for site in GLOBAL_SITES + JAPANESE_SITES + RUSSIAN_SITES:
    if site not in WEBSITES:
        WEBSITES.append(site)

# ────────────────────────────  SHARED STATE  ───────────────────────────────
SSL_CTX = ssl.create_default_context()
stop_event = threading.Event()
print_lock = threading.Lock()
seen_certs = {}          # site -> "CN=...; Issuer=..."
seen_certs_lock = threading.Lock()

stats = {
    "total":   0,
    "success": 0,
    "failed":  0,
    "latencies": deque(maxlen=ROLLING_WINDOW),
    "tls_hs":    deque(maxlen=ROLLING_WINDOW),
    "by_mode":   {},     # mode -> [ok, fail]
    "per_site":  {},     # site -> [ok, fail, total_ms]
}
stats_lock = threading.Lock()

# --- dead site skipping support ---
skip_enabled = True
failure_threshold = 3
ban_duration = 60.0
skip_lock = threading.Lock()
consecutive_failures = {}        # site -> count
banned_until = {}                # site -> expiry (monotonic time)

# ────────────────────────────  PING MODES  ────────────────────────────────

def ping_icmp(site: str, timeout: float) -> dict:
    """Shell out to system `ping`. Works without root on most platforms."""
    result = {"site": site, "mode": "ICMP", "code": None, "ms": 0.0,
              "err": None, "tls_ms": None, "extra": ""}

    is_win = platform.system().lower().startswith("win")
    count_flag = "-n" if is_win else "-c"
    wait_flag  = "-w" if is_win else "-W"
    wait_val   = str(int(timeout * 1000)) if is_win else str(int(timeout))

    cmd = ["ping", count_flag, "1", wait_flag, wait_val, site]
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout + 1,
        )
        out = proc.stdout + proc.stderr
        if proc.returncode == 0:
            m = re.search(r"time[=<]\s*([\d.]+)\s*ms", out)
            if m:
                result["ms"] = float(m.group(1))
                result["code"] = "REPLY"
            else:
                result["ms"] = (time.perf_counter() - t0) * 1000
                result["code"] = "REPLY"
        else:
            result["err"] = "UNREACH"
            result["ms"] = (time.perf_counter() - t0) * 1000
    except subprocess.TimeoutExpired:
        result["err"] = "TIMEOUT"
        result["ms"] = timeout * 1000
    except FileNotFoundError:
        result["err"] = "NO_PING"
    except Exception as e:
        result["err"] = type(e).__name__[:8].upper()
    return result


def ping_http(site: str, timeout: float, use_tls: bool) -> dict:
    """HTTP or HTTPS HEAD request. For HTTPS, measures TLS handshake separately."""
    mode = "HTTPS" if use_tls else "HTTP"
    result = {"site": site, "mode": mode, "code": None, "ms": 0.0,
              "err": None, "tls_ms": None, "extra": ""}

    # For HTTPS, do a manual TLS handshake first to time it
    if use_tls:
        try:
            t_dns = time.perf_counter()
            addr = socket.gethostbyname(site)
            t_tcp = time.perf_counter()
            with socket.create_connection((addr, 443), timeout=timeout) as sock:
                t_tls_start = time.perf_counter()
                with SSL_CTX.wrap_socket(sock, server_hostname=site) as tls:
                    t_tls_end = time.perf_counter()
                    result["tls_ms"] = (t_tls_end - t_tls_start) * 1000
                    cert = tls.getpeercert()
                    # Cache cert summary for first-seen display
                    with seen_certs_lock:
                        if site not in seen_certs and cert:
                            subj = dict(x[0] for x in cert.get("subject", []))
                            issr = dict(x[0] for x in cert.get("issuer", []))
                            cn = subj.get("commonName", "?")
                            ca = issr.get("organizationName", issr.get("commonName", "?"))
                            seen_certs[site] = f"CN={cn} / CA={ca}"
                            result["extra"] = f"🔐 {seen_certs[site]}"
        except Exception as e:
            result["err"] = type(e).__name__[:8].upper()
            result["ms"] = (time.perf_counter() - t_dns) * 1000 if 't_dns' in locals() else 0
            return result

    scheme = "https" if use_tls else "http"
    url = f"{scheme}://{site}"
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", "Mozilla/5.0 (Pinger/3.0)")
    req.add_header("Accept", "*/*")

    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=timeout) as r:
            result["code"] = r.status
    except urllib.error.HTTPError as e:
        result["code"] = e.code
    except Exception as e:
        result["err"] = type(e).__name__[:8].upper()
    result["ms"] = (time.perf_counter() - t0) * 1000
    return result


def dispatch_ping(site: str, mode: str, timeout: float) -> dict:
    """Route to the right ping function based on mode."""
    if mode == "icmp":
        return ping_icmp(site, timeout)
    if mode == "http":
        return ping_http(site, timeout, use_tls=False)
    if mode == "https":
        return ping_http(site, timeout, use_tls=True)
    if mode == "all":
        return dispatch_ping(site, random.choice(["icmp", "http", "https"]), timeout)
    raise ValueError(f"Unknown mode: {mode}")

# ───────────────────────  RESULT HANDLER & PRINTER  ────────────────────────
def mode_badge(mode):
    colors = {"HTTPS": MAGENTA, "HTTP": BLUE, "ICMP": CYAN}
    return f"{colors.get(mode, '')}{mode:<5}{RESET}"

def status_badge(code, err):
    if err:                return f"{RED}✗ {err:<8}{RESET}"
    if code == "REPLY":    return f"{GREEN}✓ REPLY   {RESET}"
    if code is None:       return f"{RED}✗ FAIL    {RESET}"
    if 200 <= code < 300:  return f"{GREEN}✓ {code}     {RESET}"
    if 300 <= code < 400:  return f"{CYAN}⟳ {code}     {RESET}"
    if 400 <= code < 500:  return f"{YELLOW}! {code}     {RESET}"
    return f"{RED}✗ {code}     {RESET}"

def latency_color(ms):
    if ms < 200: return GREEN
    if ms < 600: return YELLOW
    return RED

def is_ok(r):
    if r["err"]: return False
    c = r["code"]
    if c == "REPLY": return True
    if isinstance(c, int): return 200 <= c < 400
    return False

def on_result(fut):
    try:
        r = fut.result()
    except Exception:
        return

    ok = is_ok(r)
    site = r["site"]

    # --- dead site skipping: update consecutive failure / ban logic ---
    if skip_enabled:
        with skip_lock:
            if ok:
                # success: reset consecutive failures for this site
                if site in consecutive_failures:
                    consecutive_failures[site] = 0
            else:
                # failure: increment and possibly ban
                consec = consecutive_failures.get(site, 0) + 1
                consecutive_failures[site] = consec
                if consec >= failure_threshold and site not in banned_until:
                    banned_until[site] = time.monotonic() + ban_duration
                    with print_lock:
                        print(f"{DIM}⚠️  Skipping site {site} for {ban_duration}s due to {consec} consecutive failures{RESET}")

    with stats_lock:
        stats["total"] += 1
        stats["success" if ok else "failed"] += 1
        stats["latencies"].append(r["ms"])
        if r.get("tls_ms") is not None:
            stats["tls_hs"].append(r["tls_ms"])
        bm = stats["by_mode"].setdefault(r["mode"], [0, 0])
        bm[0 if ok else 1] += 1
        ps = stats["per_site"].setdefault(site, [0, 0, 0.0])
        ps[0 if ok else 1] += 1
        ps[2] += r["ms"]
        n = stats["total"]
        rolling_avg = statistics.mean(stats["latencies"])
        sr = stats["success"] / n * 100

    ts = datetime.now().strftime("%H:%M:%S")
    tls_part = ""
    if r.get("tls_ms") is not None:
        tls_part = f" {DIM}tls{RESET}{latency_color(r['tls_ms'])}{r['tls_ms']:4.0f}{RESET}"

    line = (
        f"{GREY}[{ts}]{RESET} "
        f"{BOLD}#{n:<4}{RESET} "
        f"{mode_badge(r['mode'])} "
        f"{status_badge(r['code'], r['err'])} "
        f"{BLUE}{site:<22}{RESET} "
        f"{latency_color(r['ms'])}{r['ms']:6.0f}ms{RESET}"
        f"{tls_part} "
        f"{DIM}│{RESET} "
        f"{GREEN}✓{stats['success']}{RESET} "
        f"{RED}✗{stats['failed']}{RESET} "
        f"{DIM}│ sr {sr:5.1f}% avg {rolling_avg:4.0f}ms{RESET}"
    )
    if r.get("extra"):
        line += f"  {DIM}{r['extra']}{RESET}"

    with print_lock:
        print(line, flush=True)
        if n % SUMMARY_EVERY == 0:
            print_summary(brief=True)

def print_summary(brief=False):
    with stats_lock:
        n = stats["total"]
        if n == 0: return
        lats = list(stats["latencies"])
        tls  = list(stats["tls_hs"])
        succ = stats["success"]; fail = stats["failed"]
        by_mode = dict(stats["by_mode"])
        per_site = dict(stats["per_site"])

    avg = statistics.mean(lats) if lats else 0
    mn  = min(lats) if lats else 0
    mx  = max(lats) if lats else 0
    med = statistics.median(lats) if lats else 0
    sr  = succ / n * 100

    bar = "━" * 72
    print(f"\n{MAGENTA}{bar}{RESET}")
    print(f"{BOLD}  📊  ROLLING STATS  (window {len(lats)}, total {n}){RESET}")
    print(f"{MAGENTA}{bar}{RESET}")
    print(f"  success rate : {GREEN}{sr:5.1f}%{RESET}  "
          f"✓ {GREEN}{succ}{RESET}   ✗ {RED}{fail}{RESET}")
    print(f"  latency (ms) : min {GREEN}{mn:.0f}{RESET}  "
          f"med {YELLOW}{med:.0f}{RESET}  "
          f"avg {YELLOW}{avg:.0f}{RESET}  "
          f"max {RED}{mx:.0f}{RESET}")
    if tls:
        print(f"  tls handshake: avg {MAGENTA}{statistics.mean(tls):.0f}ms{RESET}  "
              f"min {statistics.min(tls) if False else min(tls):.0f}  "
              f"max {max(tls):.0f}  ({len(tls)} samples)")

    if by_mode:
        print(f"  by mode      : ", end="")
        for m, (ok, ko) in by_mode.items():
            tot = ok + ko
            pct = ok / tot * 100 if tot else 0
            print(f"{mode_badge(m)} {ok}/{tot} ({pct:.0f}%)  ", end="")
        print()

    if not brief and per_site:
        averages = [
            (s, d[2] / max(1, d[0] + d[1]), d[0], d[1])
            for s, d in per_site.items() if (d[0] + d[1]) >= 2
        ]
        if averages:
            averages.sort(key=lambda x: x[1])
            print(f"\n  {BOLD}⚡ Fastest:{RESET}")
            for s, a, ok, ko in averages[:3]:
                print(f"    {GREEN}{a:6.0f}ms{RESET}  {s}  ({ok}✓/{ko}✗)")
            print(f"  {BOLD}🐢 Slowest:{RESET}")
            for s, a, ok, ko in averages[-3:][::-1]:
                print(f"    {RED}{a:6.0f}ms{RESET}  {s}  ({ok}✓/{ko}✗)")
    print(f"{MAGENTA}{bar}{RESET}\n")

# ─────────────────────────  SIGNAL HANDLING  ─────────────────────────────
def handle_signal(signum, _frame):
    stop_event.set()

signal.signal(signal.SIGINT,  handle_signal)
signal.signal(signal.SIGTERM, handle_signal)
try:
    signal.signal(signal.SIGHUP, handle_signal)
except AttributeError:
    pass

# ────────────────────────  FLAG SELECTION MENU  ─────────────────────────
def interactive_flag_menu(args):
    """Display a menu to modify runtime flags (skip, thresholds, interval, timeout, workers)."""
    changed = False

    while True:
        print(f"\n{BOLD}{CYAN}⚙️  FLAG / OPTION CONFIGURATION{RESET}")
        print(f"{DIM}Adjust the behaviour of the pinger (current values shown):{RESET}\n")
        print(f"  {BOLD}1.{RESET}  Skip unreachable sites            : {GREEN if args.skip_unreachable else RED}{args.skip_unreachable}{RESET}")
        print(f"      {DIM}→ automatically ban sites after N consecutive failures{RESET}")
        print(f"  {BOLD}2.{RESET}  Failure threshold (consecutive)  : {YELLOW}{args.failure_threshold}{RESET}")
        print(f"      {DIM}→ number of fails before temporary ban{RESET}")
        print(f"  {BOLD}3.{RESET}  Ban duration (seconds)           : {YELLOW}{args.ban_duration}{RESET}")
        print(f"      {DIM}→ how long a site stays banned{RESET}")
        print(f"  {BOLD}4.{RESET}  Ping interval (seconds)          : {YELLOW}{args.interval}{RESET}")
        print(f"      {DIM}→ delay between consecutive ping launches{RESET}")
        print(f"  {BOLD}5.{RESET}  Request timeout (seconds)        : {YELLOW}{args.timeout}{RESET}")
        print(f"      {DIM}→ max time to wait for a response{RESET}")
        print(f"  {BOLD}6.{RESET}  Concurrent workers               : {YELLOW}{args.workers}{RESET}")
        print(f"      {DIM}→ number of parallel ping requests{RESET}")
        print(f"\n  {BOLD}7.{RESET}  ✅  Done – continue with current settings")
        print(f"  {BOLD}0.{RESET}  ❌  Quit")

        choice = input(f"\n{BOLD}➜ select an option (1-7, 0): {RESET}").strip()

        if choice == "0":
            print(f"{YELLOW}Bye!{RESET}")
            sys.exit(0)
        elif choice == "1":
            args.skip_unreachable = not args.skip_unreachable
            print(f"→ Skip unreachable set to {args.skip_unreachable}")
            changed = True
        elif choice == "2":
            try:
                val = int(input("  New failure threshold (>=1): "))
                if val >= 1:
                    args.failure_threshold = val
                    changed = True
                else:
                    print(f"{RED}Must be at least 1.{RESET}")
            except ValueError:
                print(f"{RED}Invalid number.{RESET}")
        elif choice == "3":
            try:
                val = float(input("  New ban duration (seconds, >0): "))
                if val > 0:
                    args.ban_duration = val
                    changed = True
                else:
                    print(f"{RED}Must be positive.{RESET}")
            except ValueError:
                print(f"{RED}Invalid number.{RESET}")
        elif choice == "4":
            try:
                val = float(input("  New ping interval (seconds, >=0.2): "))
                if val >= 0.2:
                    args.interval = val
                    changed = True
                else:
                    print(f"{RED}Interval too small (minimum 0.2s).{RESET}")
            except ValueError:
                print(f"{RED}Invalid number.{RESET}")
        elif choice == "5":
            try:
                val = float(input("  New request timeout (seconds, >=1): "))
                if val >= 1:
                    args.timeout = val
                    changed = True
                else:
                    print(f"{RED}Timeout must be at least 1 second.{RESET}")
            except ValueError:
                print(f"{RED}Invalid number.{RESET}")
        elif choice == "6":
            try:
                val = int(input("  New concurrent workers (1-64): "))
                if 1 <= val <= 64:
                    args.workers = val
                    changed = True
                else:
                    print(f"{RED}Workers must be between 1 and 64.{RESET}")
            except ValueError:
                print(f"{RED}Invalid number.{RESET}")
        elif choice == "7":
            break
        else:
            print(f"{RED}Invalid choice, please enter 0-7.{RESET}")

    # Sync global skip variables
    global skip_enabled, failure_threshold, ban_duration
    skip_enabled = args.skip_unreachable
    failure_threshold = args.failure_threshold
    ban_duration = args.ban_duration

    if changed:
        print(f"{GREEN}✓ Flags updated.{RESET}")
    return args

# ─────────────────────────────  MAIN  ────────────────────────────────────
def interactive_menu():
    """Show an interactive menu to pick the ping mode. Returns the chosen mode."""
    options = [
        ("all",   "🎲  ALL      — random mix of ICMP, HTTP, and HTTPS"),
        ("https", "🔐  HTTPS    — TLS handshake timing + cert inspection"),
        ("http",  "🌐  HTTP     — plain HTTP HEAD requests"),
        ("icmp",  "📡  ICMP     — classic ping (uses system ping command)"),
    ]
    print(f"""{BOLD}{CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║   🌐  WEBSITE PING SCRAMBLER PRO                                             ║
║        by Seth Khaneki's — Azazel                                            ║
║        ICMP + HTTP + HTTPS · Select a ping mode to begin                     ║
╚══════════════════════════════════════════════════════════════════════════════╝{RESET}
""")
    print(f"  {BOLD}Choose a mode:{RESET}\n")
    for i, (_, label) in enumerate(options, 1):
        print(f"    {BOLD}{CYAN}[{i}]{RESET}  {label}")
    print(f"    {BOLD}{CYAN}[q]{RESET}  ❌  Quit\n")
    print(f"  {DIM}(default: 1 — press Enter to accept){RESET}")

    while True:
        try:
            choice = input(f"\n  {BOLD}➜ your pick: {RESET}").strip().lower()
        except EOFError:
            choice = ""
        if choice == "":
            return options[0][0]
        if choice in ("q", "quit", "exit"):
            print(f"{YELLOW}Bye!{RESET}")
            sys.exit(0)
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1][0]
        for key, _ in options:
            if choice == key:
                return key
        print(f"  {RED}✗ Invalid choice — enter 1-{len(options)} or q{RESET}")

def parse_args():
    p = argparse.ArgumentParser(description="Website Ping Scrambler Pro by Seth Khaneki's - Azazel — ICMP/HTTP/HTTPS")
    p.add_argument("--mode", choices=["icmp", "http", "https", "all"],
                   default=None, help="Ping mode (skips interactive menu if set)")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                   help=f"Seconds between pings (default: {DEFAULT_INTERVAL})")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                   help=f"Per-request timeout (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                   help=f"Concurrent workers (default: {DEFAULT_WORKERS})")
    p.add_argument("--skip-unreachable", dest="skip_unreachable", action="store_true",
                   default=True, help="Enable skipping of sites that repeatedly fail (default: enabled)")
    p.add_argument("--no-skip-unreachable", dest="skip_unreachable", action="store_false",
                   help="Disable skipping of failing sites")
    p.add_argument("--failure-threshold", type=int, default=3,
                   help="Number of consecutive failures before banning a site (default: 3)")
    p.add_argument("--ban-duration", type=float, default=60.0,
                   help="Seconds to ban a site after threshold is reached (default: 60)")
    return p.parse_args()

def get_active_sites():
    """Return a list of sites that are not currently banned (using skip_lock)."""
    with skip_lock:
        now = time.monotonic()
        expired = [s for s, exp in banned_until.items() if exp <= now]
        for s in expired:
            del banned_until[s]
            if s in consecutive_failures:
                consecutive_failures[s] = 0
            with print_lock:
                print(f"{DIM}🔁  Site {s} re-enabled after ban{RESET}")
        active = [site for site in WEBSITES if site not in banned_until]
        if not active:
            if not hasattr(get_active_sites, "warned"):
                get_active_sites.warned = True
                with print_lock:
                    print(f"{YELLOW}⚠️  All sites are currently banned, falling back to full list{RESET}")
            return WEBSITES[:]
        return active

def main():
    global skip_enabled, failure_threshold, ban_duration
    args = parse_args()

    if args.mode is None:
        args.mode = interactive_menu()

    # Show flag configuration menu after mode selection
    args = interactive_flag_menu(args)

    banner = f"""{BOLD}{CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║   🌐  WEBSITE PING SCRAMBLER PRO                                             ║
║        by Seth Khaneki's — Azazel  ·  ICMP + HTTP + HTTPS                    ║
║   mode: {args.mode:<6} · interval: {args.interval:>4.1f}s · workers: {args.workers:>3} · pool: {len(WEBSITES):>3} sites       ║
║   skip unreachable: {str(args.skip_unreachable):<5} (thresh={args.failure_threshold} · ban={args.ban_duration}s)          ║
║   Press Ctrl+C (or close terminal) to stop                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner, flush=True)

    pool = ThreadPoolExecutor(max_workers=args.workers, thread_name_prefix="pinger")
    next_tick = time.monotonic()

    try:
        while not stop_event.is_set():
            if skip_enabled:
                active_sites = get_active_sites()
                site = random.choice(active_sites)
            else:
                site = random.choice(WEBSITES)

            fut = pool.submit(dispatch_ping, site, args.mode, args.timeout)
            fut.add_done_callback(on_result)

            next_tick += args.interval
            sleep_for = next_tick - time.monotonic()
            if sleep_for > 0:
                stop_event.wait(timeout=sleep_for)
            else:
                next_tick = time.monotonic()
    finally:
        print(f"\n{YELLOW}⏳ Draining in-flight requests…{RESET}", flush=True)
        pool.shutdown(wait=True, cancel_futures=True)
        print_summary(brief=False)
        print(f"{BOLD}{GREEN}👋  Goodbye.{RESET}")

if __name__ == "__main__":
    main()