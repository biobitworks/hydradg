.PHONY: newinml-reproduce newinml-verify newinml-build

newinml-reproduce: newinml-build newinml-verify

newinml-build:
	python3 scripts/build_successor_recovery.py

newinml-verify:
	python3 scripts/reproduce_newinml.py --verify
