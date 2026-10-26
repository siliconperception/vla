default:
	echo "make {build,upload}"

build:
	echo "remember to bump version in both __init.py__ and pyproject.toml"
	rm -rf dist/*
	python3 -m build --verbose --wheel

upload:
	twine upload dist/*
