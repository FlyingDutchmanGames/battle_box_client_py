# Devloping the Client

## Running the Specs

Use unittest to run the specs (only one file for now)
```
python3 -m unittest tests/client_test.py
```

## Running the formatter

```
python3 -m autopep8 --in-place --aggressive --aggressive {file name}
```

Or run them all (this may need changes over time)
```
find . | grep .py | grep -v .pyc | xargs python3 -m autopep8 --in-place --aggressive --aggressive
```

## Uploading

```
# Build It
python3 setup.py sdist bdist_wheel

# Test registry
# python3 -m twine upload --repository testpypi dist/*

# Real Index
# python3 -m twine upload dist/*
```
