PY = PYTHONPATH=. .venv/bin/python
VERSION ?= v0

# M0: run all tasks ONCE and print the success rate.
eval:
	$(PY) -m evals.runner --version $(VERSION) --trials 1 --run-id $(VERSION)-once --workers $${WORKERS:-2}
	$(PY) -m evals.grade $(VERSION)-once --no-judge

# M1: full run, n = 4 trials per task, then grade and report.
run:
	$(PY) -m evals.runner --version $(VERSION) --trials 4 --run-id $(VERSION) --workers $${WORKERS:-2}
	$(PY) -m evals.grade $(VERSION)
	$(PY) -m evals.report $(VERSION)

test:
	$(PY) -m pytest -q tests
