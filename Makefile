.phony: all
all: sync run

.phony: sync
sync:
	rsync -r --size-only "alex@nas.local:/volume1/media/music/" "./music"

.phony: run
run: venv/bin/python
	./export.py

venv/bin/python:
	$(shell which python) -m venv ./venv
	./venv/bin/pip install -q -U pip
	./venv/bin/pip install -q -U ffmpeg-python

.phony: clean
clean:
	rm -rf ./venv/
	rm -rf ./export/*
