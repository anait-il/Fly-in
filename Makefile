PY = python3

UV = uv

MAIN = main.py

FLAGS = --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

run :
	@$(UV) run $(PY) $(MAIN)

install :
	@$(UV) sync

debug :
	@$(UV) run $(PY) -m pdb $(MAIN)

clean :
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint :
	@flake8 .
	@mypy .  $(FLAGS)
