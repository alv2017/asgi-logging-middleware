# Changelog

This document keeps track of the changes made to the project.

## [0.2.0] - [2025-11-07]

### Added
- New feature: `cpu_time` is added as a logging option to log CPU time used for each request.

### Fixed
- `time.time()` replaced with `time.perf_counter()` for more accurate timing of requests.
- Minor fixes to existing tests
