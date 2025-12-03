# 🚀 **RockSec’s Fast Style Multi-Domain Web Fuzzer**

A high-performance, multi-domain web fuzzer, designed for bug bounty, reconnaissance, directory discovery, and endpoint enumeration.

This tool delivers **speed**, **control**, and **clean output**, making it ideal for large engagement scans.

---

# 📌 **Features**

### ⚡ High-Speed Scanning

* Multi-threaded engine (80–200+ threads)
* Connection pooling for maximum throughput
* On-the-fly variant generation (no “freeze” at startup)
* Bypass payloads + extension permutations

### 🎯 Precision Output Control

* Print only selected HTTP status codes using:

  ```
  --status 200,403,302
  ```
* Save **only** these codes (built-in):

  ```
  200, 302, 403, 401
  ```

### 🌐 Multi-Domain Support

* Accepts:

  * Single domain
  * Text file with many domains
* Reuses optimized scanning logic for each domain

### 📄 Wordlist Directory

Fully supports a directory containing multiple wordlist files:

```
./wordlists/
  ├── common.txt
  ├── admin.txt
  └── leaks.txt
```

### 📊 Live Progress Bar (Dirsearch-Style)

Real-time stats:

```
[PROGRESS] Words left: 2012/5000 | RPS: 154.7 | Hits: 17 | ETA: 00:02
```

Displays:

* Remaining words
* Requests per second
* Hits found
* Time estimate

### 📝 Smart Output File Naming (Option 2)

* If scanning a **domain list file**:

```
targets.txt → targets.txt
```

* If scanning **single domain**:

```
https://example.com → example.com.txt
```

### ✔ Clean, Colorized Output

```
[14:22:31] 200   523B   GET      https://example.com/admin
[14:22:32] 403     0B   GET      https://example.com/.git/
[14:22:33] 302     0B   GET      https://example.com/login  --> /auth/
```

---

# 🏁 **Installation**

### Requirements:

* Python **3.8+**
* `requests` and `colorama` packages

Install dependencies:

```bash
pip install requests colorama
```

Make script executable (optional):

```bash
chmod +x Fuzzing.py
```

---

# 🧩 **Usage**

## Basic Usage (Single Domain)

```bash
python3 Fuzzing.py https://example.com ./wordlists/
```

Output saved to:

```
example.com.txt
```

---

## Multi-Domain Scan

Put multiple domains in a file:

**domains.txt**

```
https://example.com
https://test.com/app
https://admin.site.org
```

Then scan:

```bash
python3 Fuzzing.py domains.txt ./wordlists/
```

Output saved to:

```
domains.txt
```

---

## Print Only Specific Status Codes

Show only 200, 302, 403 on screen:

```bash
python3 Fuzzing.py https://example.com ./wordlists/ --status 200,302,403
```

---

## High Speed Mode (Recommended)

```bash
python3 Fuzzing.py https://example.com ./wordlists/ --threads 150 --timeout 4
```

---

# 🎛 **Command Reference (Help Details)**

```
Usage:
  Fuzzing.py <target|target_file> <wordlist_dir> [options]

Arguments:
  <target>            Single URL (ex: https://example.com)
  <target_file>       File containing URLs (one per line)
  <wordlist_dir>      Directory with one or more wordlist files
```

---

## Options

### General:

```
-t, --threads N       Number of threads (default: 80)
--timeout N           Request timeout in seconds (default: 5)
--insecure            Disable SSL verification
```

### Request Controls:

```
--proxy URL           Use HTTP/S proxy
--headers JSON        Add custom headers
```

Example:

```
--headers '{"User-Agent":"Custom","X-Token":"123"}'
```

### Output Control:

```
--status 200,403      Print ONLY these status codes
```

If omitted → prints ALL responses.

### Saving Behavior:

Always saves only:

```
200, 302, 403, 401
```

No configuration needed.

---

# 📝 **What Gets Saved to File**

The tool writes this format:

```
<status> - <size>B - <url>
```

Example:

```
200 - 523B - https://example.com/admin
403 -   0B - https://example.com/.git/
302 -   0B - https://example.com/login
```

---

# 📊 **Progress Bar Explanation**

Example:

```
[PROGRESS] Words left: 1800/5000 | RPS: 135.2 | Hits: 11 | ETA: 00:02
```

| Metric     | Meaning                    |
| ---------- | -------------------------- |
| Words left | Wordlist entries remaining |
| RPS        | Requests per second        |
| Hits       | Count of saved results     |
| ETA        | Estimated time remaining   |

---

# 🔧 **How Fuzzying Works Internally**

For each word:

* Append extensions:

  ```
  .php, .bak, .json, .env, etc.
  ```
* Append bypass techniques:

  ```
  %, %2e/, ;/, //, ../
  ```
* Generate variants *on the fly* (super fast)
* Send HTTP GET
* Process responses
* Apply filters (print only / save only)

Designed to be **fast, direct, and stable**.

---

# ⚠ Legal Disclaimer

This tool is intended **only** for legal penetration testing
or security research on systems you are authorized to test.

Unauthorized scanning is illegal.

---

# 🧑‍💻 Author

**RockSec**

Built with care for speed, reliability, and practical bug bounty usage.

---
