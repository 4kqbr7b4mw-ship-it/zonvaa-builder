# Local eval harness

`run_local.py` loads `cases.jsonl`, exercises the real deterministic manager
path or the real boundary/configuration component named by the case, writes
`results/latest.json`, and exits non-zero when a behavioral assertion fails.
It performs no API call and must not be described as a model-quality eval.
