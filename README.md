# general-go-project-template

Template of golang project which uses [Python Invoke](http://www.pyinvoke.org/) as replacement of Makefile

## Python requirements Installation

To install required python modules execute:

```bash
pip install -r requirements.txt
```

### Golang Packages

This skeleton contains a file `dependencies.txt` which has dependencies separated by `\n`. 

To install packages:

```bash
invoke get --install
```

### Test

To test

```bash
invoke test_fast --module=project --cpu=8
```

### Run

To execute a project

```bash
invoke start_fast
```

### Build binary

```bash
invoke build
```
