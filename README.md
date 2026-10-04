# pytigon-standard-prj

The **standard projects and applications** for Pytigon — the blocks that Pytigon
systems are assembled from.

## Install

Do not install this package directly. It is pulled in automatically by the two
runnable packages:

| Package | Role |
|---|---|
| `pytigon-batteries` | web server — installs this package |
| `pytigon-gui` | desktop application — installs this package (through `pytigon-batteries`) |

```
pip install pytigon-batteries   # web server, includes the standard projects
pip install pytigon-gui         # desktop application, same projects
```

The base `pytigon` package does **not** depend on it, because it is a library
rather than a runnable install: a custom, reduced system may provide its own
projects instead.

## License

LGPL-2.1 © Sławomir Chołaj
