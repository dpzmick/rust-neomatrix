#!/usr/bin/env python2
import re
import sys

# read from stdin, convert `cargo bench` output to csv

# shamelessly ripped off from BurntSushi/cargo-benchcmp
BENCHMARK_REGEX = (
"test\s+(?P<name>\S+)\s+...\sbench:\s+(?P<ns>[0-9,]+)\s+ns/iter"
"\s+\(\+/-\s+(?P<variance>[0-9,]+)\)"
)

if __name__ == "__main__":
    print 'test_name,nanoseconds,variance'
    for line in sys.stdin:
        matches = re.search(BENCHMARK_REGEX, line)
        if matches is not None:
            print ','.join([m.replace(',', '') for m in matches.groups()])
