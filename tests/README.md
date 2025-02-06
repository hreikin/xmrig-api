# Tests

This directory contains tests for the XMRig API. These tests use mocked data to simulate miner responses. These tests do not require a live miner instance and can be run in isolation or all together.

## Usage

These tests should be run from the project root, they can be run all at once or individually:

```python
# All together
python -m unittest tests/test*.py
# Individually
python -m unittest tests/test_api.py
```