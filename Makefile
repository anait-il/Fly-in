PY = python3

UV = uv run

MAIN = main.py

FLAGS = --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

run :
	@$(UV) $(PY) $(MAIN)

install :
	@$(UV) sync
