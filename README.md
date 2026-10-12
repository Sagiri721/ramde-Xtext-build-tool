# RAMDE in python!

Current models available:

- `projdsl` for requirements, risks, and requirement relationships (`.projdsl`)
- `ucdsl` for use cases and actors, including use-case refinements (`.ucdsl`)

## Requirements

- Python
- Java
- PlantUML, jar should be included in `tools/plantuml*.jar`
- Graphviz `dot` for the default `dot` layout; alternatively, use the built-in `smetana` layout without Graphviz

PlantUML source (`.puml`) can be generated without Java or Graphviz by disabling SVG output.

## Install

From the project root, create and activate a virtual environment, then install the project in editable mode:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

```sh
ramde health
```

The `health` command reports registered languages and the Java, PlantUML, and Graphviz tools it can find. Graphviz is optional if you select `smetana`.

## Generate Diagrams

Build every model found recursively under `03_models/`:

```sh
ramde build
```

By default, generated files go to `01_documentation/generated/`. For example, a model named `sample_smarthome.ucdsl` produces `sample_smarthome.ucdsl.puml` and `sample_smarthome.ucdsl.svg`. You can also pass model files or folders and choose another output folder:

```sh
ramde build 03_models/sample_smarthome.projdsl 03_models/sample_smarthome.ucdsl
ramde build 03_models --out build/diagrams
```

Useful options:

```sh
ramde build --help
ramde build --layout smetana
ramde build --no-svg
ramde build --links none
```

The default `dot` layout uses Graphviz. `--layout smetana` uses PlantUML's built-in layout engine. SVG generation is on by default; `--no-svg` writes only `.puml` files. The CLI's default `--links vscode` makes diagram nodes clickable links to source lines; use `--links none` for plain labels.

To rebuild after model edits, run:

```sh
ramde watch
```

Watch accepts the same input and output options as `build`. Press Ctrl+C to stop it. Grammar changes in `03_metamodels/` require restarting the watcher.

## textX Commands

The grammars and generators are registered when the project is installed. You can validate individual files and generate a diagram directly with textX:

```sh
textx check 03_models/sample_smarthome.projdsl
textx check 03_models/sample_smarthome.ucdsl
textx generate 03_models/sample_smarthome.ucdsl --target plantuml
textx generate 03_models/sample_smarthome.ucdsl --target svg --links vscode -o out/
```

## Adding a DSL

The registry automatically discovers Python modules in `src/core/data/` that export a `SPEC`. To add a built-in DSL:

1. Add its grammar under `02_metamodels/`.
2. Add `src/core/data/<name>.py` with its `DSLSpec`, metamodel configuration, validation, and any reference scoping.
3. Add its renderer under `src/core/data/presentation/` and reference it from the spec; every DSL included in `ramde build` must provide one.
4. Add the language and generator entry points in `pyproject.toml`. textX requires these packaging entries so its CLI can discover each language and target.

Run tests with the development dependency installed:

```sh
python -m pytest
```