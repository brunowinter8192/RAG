<!-- source: https://docs.searxng.org/dev/engines/online/alpinelinux.html -->

# Alpine Linux Packages
[Alpine Linux binary packages](https://pkgs.alpinelinux.org). [Alpine Linux](https://www.alpinelinux.org) is a Linux-based operation system designed to be small, simple and secure. Contrary to many other Linux distributions, it uses musl, BusyBox and OpenRC. Alpine is mostly used on servers and for Docker images. 

**engines.alpinelinux.alpine_arch** = `'x86_64'`
Kernel architecture: `x86_64`, `x86`, `aarch64`, `armhf`, `ppc64le`, `s390x`, `armv7` or `riscv64` 

**engines.alpinelinux.ARCH_RE** = `re.compile('x86_64|x86|aarch64|armhf|ppc64le|s390x|armv7|riscv64')`
Regular expression to match supported architectures in the query string.
