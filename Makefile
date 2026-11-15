PYTHON ?= python3

.PHONY: quality test lint typecheck security dependency-audit package-check shell-check

quality: test lint typecheck security dependency-audit package-check shell-check

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	ruff check src tests scripts/check-wheel.py
	ruff format --check src tests scripts/check-wheel.py

typecheck:
	mypy src/homelab_ops scripts/check-wheel.py

security:
	bandit -r src/homelab_ops

dependency-audit:
	pip-audit -r requirements-quality.txt

package-check:
	$(PYTHON) -m build --wheel --outdir build
	$(PYTHON) scripts/check-wheel.py build/*.whl

shell-check:
	@for script in scripts/*.sh; do sh -n "$$script" || exit $$?; done
