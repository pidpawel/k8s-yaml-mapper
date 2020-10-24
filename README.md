# K8s-YAML-mapper

[yaml-to-dhall](https://github.com/dhall-lang/dhall-haskell/tree/master/dhall-yaml)
is in general unable to parse regular `.yml` files distributed by various
projects designed to work on Kubernetes. This script is one way of fixing that.
It **parses the usual stream of YAML documents**, extracts their `namespace`,
`name` and `kind` and generates a **YAML dictionary as a single document** that
you can feed to `yaml-to-dhall`.

**This software is not battle tested by any means.** Please do report bugs, pull
requests are welcome too.

## Usage

1. Install pipenv or project dependencies

`pip install --user pipenv`

or

`pyyaml` and `click` for Python 3.

2. Run the script

`pipenv run python k8s-yaml-mapper.py --verify scw.yaml scw-out.yml`

No output means good.

`--verify` flag makes sure there are no duplicates and no missing objects.

`--nested` flag makes the script create multi level dictionary (one for
`namespace`, `name` and `kind`).

`--separator` when you're not using `--nested` it allows you to change the
separator for name components.
