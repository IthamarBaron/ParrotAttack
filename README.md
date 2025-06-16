# Parrot Attack

Parrot Attack is a remake of a long-lost high school script. It is designed to prank/stress-test a Windows PC in a obnoxious and network-abusing fashion. The program heavily consumes CPU resources and generates significant TCP traffic. **Do not run this unless you know exactly what you're doing.**

---

## How It Works

1. **CPU Managment:**

   * The program detects how many CPU cores your system has.
   * It spawns a separate process for each core.
   * Each process launches multiple threads.

2. **Threads managment:**

   * Each thread spawns a cmd that runs `curl parrot.live`.
   * The cmd is moved randomly across the screen in a jittery fashion.

4. **Network Load:**

   * Each parrot animation establishes a TCP connection to `parrot.live`.
   * With enough threads and processes, this floods your network stack quickly.

---

## Kill Switches

* **Time-Based:** Runs for a configurable time (`KILL_TIME`).
* **File-Based:** Drops execution if `perfc.dat` is found on the Desktop.

---

## Usage

> **Warning:** only run this in a close environment (or a school pc).


The script requires:

* Windows OS
* Python 3.x

Make sure you have `curl` available in the system path.

---

## Why?

Cause an ascii dancing parrot is cool and im annoying. :)

---

## Author Notes

This project was built mostly for laughs, nostalgia, and crashing kidron's pc

---

