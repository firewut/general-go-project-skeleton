# general-go-project-template

Template of golang project which uses [Python Invoke](http://www.pyinvoke.org/) as replacement of Makefile

## Python requirements Installation

To install required python modules execute:

```bash
pip install -r dev-tools/requirements.txt
```

### Golang Packages

This skeleton contains a file `dependencies.txt` which has dependencies separated by `\n`. 

To install packages:

```bash
invoke -r dev-tools get 
```

### Test

To test

```bash
invoke -r dev-tools test
invoke -r dev-tools test --module=project/modules/config
```

### Run

To execute a project

```bash
invoke -r dev-tools run 
```

### Build binary

```bash
invoke -r dev-tools build
```
