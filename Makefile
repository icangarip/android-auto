SHELL := /bin/bash

.PHONY: run run-fast run-2m run-5m

run:
	bash scripts/run_locator.sh -m $${MINS:-2}

run-fast:
	FAST_MODE=1 WATCH_MIN_SECS=1 WATCH_MAX_SECS=3 LOAD_SECS=0.5 \
		bash scripts/run_locator.sh -m $${MINS:-2}

run-2m:
	bash scripts/run_locator.sh -m 2

run-5m:
	bash scripts/run_locator.sh -m 5

