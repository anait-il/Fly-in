PY = python3

UV = uv run

FLAGS = --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

run : install
	$(PY) $(UV) 