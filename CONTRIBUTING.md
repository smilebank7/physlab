# Contributing

physlab is MIT-licensed and only accepts dependencies with permissive or weak
copyleft licenses approved in `tools/check_licenses.py`.

GPL, AGPL, LGPL, proprietary, unknown, and unlicensed dependencies are not
allowed in v0.1.

## Branch Protection

`main` should require the `CI / Hardware freedom / 3 OS matrix` check and the
license audit before merge. The hardware-freedom job depends on the full
`macos-14`, `macos-15`, and `ubuntu-22.04` CI matrix, so a missing or failing OS
keeps the merge gate red.
