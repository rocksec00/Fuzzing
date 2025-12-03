#!/usr/bin/env python3
# Rocky's Fast Dirsearch-Style Multi-Domain Web Fuzzer (Option 2 Output Naming)
# ⚠ For legal & authorized testing only.

import os
import sys
import json
import random
import threading
import time
import requests
from urllib.parse import urljoin
from datetime import datetime
from queue import Queue, Empty
from colorama import Fore, Style, init as color_init

color_init(autoreset=True)

DEFAULT_THREADS = 20       # fast default
DEFAULT_TIMEOUT = 3

SAVE_CODES = {200, 302, 403, 401}     # always save these

EXTENSIONS = [
    "", ".php", ".asp", ".aspx", ".jsp",
    ".bak", ".old", ".zip", ".tar", ".tar.gz",
    ".txt", ".log", ".conf", ".json", ".env"
]

BYPASS = [
    "", "/", "/.", ";/", "%2e/", "%2f",
    "/..;/", "../", "//"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
]

lock = threading.Lock()


def ts():
    return datetime.now().strftime("%H:%M:%S")


def extract_domain(url):
    return url.replace("https://", "").replace("http://", "").split("/")[0]


def color_for(code):
    if 200 <= code < 300:
        return Fore.GREEN
    if 300 <= code < 400:
        return Fore.BLUE
    if 400 <= code < 500:
        return Fore.YELLOW
    if 500 <= code < 600:
        return Fore.RED
    return Fore.WHITE


# ==========================
#          Fuzzer
# ==========================

class Fuzzer:
    def __init__(self, args, target, result_file, save_codes, print_codes):
        self.args = args
        self.base = target.rstrip("/") + "/"
        self.result_file = result_file
        self.save_codes = save_codes
        self.print_codes = print_codes

        self.session = requests.Session()
        self.session.verify = not args.insecure

        adapter = requests.adapters.HTTPAdapter(
            pool_connections=args.threads * 2,
            pool_maxsize=args.threads * 2
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers["User-Agent"] = random.choice(USER_AGENTS)

        if args.headers:
            try:
                self.session.headers.update(json.loads(args.headers))
            except:
                print(Fore.RED + "[!] Invalid --headers JSON, ignoring.")

        self.proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None

        self.queue = Queue()
        self.total_words = 0
        self.words_done = 0
        self.req_count = 0
        self.hits = 0

        self.progress_running = False
        self.start_time = None

    # --------------------------
    def load_wordlists(self):
        words = set()
        for root, _, files in os.walk(self.args.wordlist):
            for file in files:
                with open(os.path.join(root, file), "r", errors="ignore") as f:
                    for line in f:
                        w = line.strip()
                        if w:
                            words.add(w)

        for w in words:
            self.queue.put(w)

        self.total_words = self.queue.qsize()
        print(Fore.CYAN + f"[i] Base words loaded: {self.total_words}")

    # --------------------------
    def variants(self, word):
        base = word.rstrip("/")
        out = set()

        for ext in EXTENSIONS:
            out.add(base + ext)

        temp = set()
        for v in out:
            for bp in BYPASS:
                temp.add(v + bp)

        out.update(temp)
        return out

    # --------------------------
    def req(self, url):
        try:
            return self.session.get(
                url,
                timeout=self.args.timeout,
                proxies=self.proxies,
                allow_redirects=True,
            )
        except Exception:
            return None

    # --------------------------
    def handle_path(self, rel):
        url = urljoin(self.base, rel)
        r = self.req(url)
        if r is None:
            return

        code = r.status_code
        size = len(r.content)

        redirect = ""
        if 300 <= code < 400:
            loc = r.headers.get("Location")
            if loc:
                redirect = f"  -->  {loc}"

        with lock:
            self.req_count += 1

        # print filter
        should_print = (self.print_codes is None) or (code in self.print_codes)

        if should_print:
            color = color_for(code)
            with lock:
                print(
                    f"{color}[{ts()}] {code:4}  {size:5}B   GET      {url}{redirect}{Style.RESET_ALL}"
                )

        # save filter
        if code in self.save_codes:
            with lock:
                with open(self.result_file, "a") as f:
                    f.write(f"{code} - {size}B - {url}\n")
                self.hits += 1

    # --------------------------
    def worker(self):
        while True:
            try:
                word = self.queue.get(timeout=1)
            except Empty:
                return

            for v in self.variants(word):
                self.handle_path(v)

            with lock:
                self.words_done += 1

            self.queue.task_done()

    # --------------------------
    def progress_loop(self):
        while self.progress_running:
            with lock:
                done = self.words_done
                total = self.total_words
                hits = self.hits
                reqs = self.req_count
                elapsed = max(time.time() - self.start_time, 0.001)

            rps = reqs / elapsed
            remaining = total - done
            eta = remaining / (done / elapsed) if done > 0 else 0
            eta_min, eta_sec = int(eta // 60), int(eta % 60)

            sys.stdout.write(
                f"\r{Fore.CYAN}[PROGRESS] Words left: {remaining}/{total} | "
                f"RPS: {rps:6.1f} | Hits: {hits} | ETA: {eta_min:02d}:{eta_sec:02d}{Style.RESET_ALL}"
            )
            sys.stdout.flush()
            time.sleep(1)

        sys.stdout.write("\n")
        sys.stdout.flush()

    # --------------------------
    def run(self):
        print(Fore.CYAN + f"\n=== Scanning: {self.base} ===\n")

        self.load_wordlists()

        self.start_time = time.time()
        self.progress_running = True

        p = threading.Thread(target=self.progress_loop)
        p.daemon = True
        p.start()

        threads = []
        for _ in range(self.args.threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self.progress_running = False
        p.join()


# ==========================
#     CLI + Targets
# ==========================

def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="Fast Dirsearch Multi-Domain Fuzzer")

    p.add_argument("targets")
    p.add_argument("wordlist")

    p.add_argument("-t", "--threads", type=int, default=DEFAULT_THREADS)
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    p.add_argument("--proxy")
    p.add_argument("--headers")
    p.add_argument("--insecure", action="store_true")

    p.add_argument(
        "--status",
        help="Only print these status codes (e.g., 200,403). Default: print all.",
        default=""
    )

    return p.parse_args()


def load_targets(t):
    if os.path.isfile(t):
        out = []
        with open(t, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(line)
        return out, os.path.basename(t)
    return [t], extract_domain(t)


def main():
    args = parse_args()

    targets, output_name = load_targets(args.targets)

    # OPTION 2: output file is based on domainlist OR domain name
    result_file = output_name
    if not result_file.endswith(".txt"):
        result_file += ".txt"

    # parse print filter
    print_codes = None
    if args.status.strip():
        print_codes = set()
        for c in args.status.split(","):
            c = c.strip()
            if c.isdigit():
                print_codes.add(int(c))
        if not print_codes:
            print_codes = None

    print(Fore.GREEN + f"[i] Printing: {'ALL' if print_codes is None else sorted(print_codes)}")
    print(Fore.GREEN + f"[i] Saving only: {sorted(SAVE_CODES)}")
    print(Fore.GREEN + f"[i] Output file: {result_file}")

    open(result_file, "w").close()

    for t in targets:
        fuzzer = Fuzzer(args, t, result_file, SAVE_CODES, print_codes)
        fuzzer.run()

    print(Fore.GREEN + f"\n[+] Results written to {result_file}")


if __name__ == "__main__":
    main()
