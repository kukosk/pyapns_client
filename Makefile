build:
	python -m build

publish: build
	python -m pip install --upgrade twine \
	&& python -m twine upload dist/*

clean:
	rm -rf dist/

.PHONY: build publish clean 
