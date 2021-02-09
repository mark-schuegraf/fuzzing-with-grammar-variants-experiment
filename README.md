# Grammar Transformations

Exploring how transforming grammars affects grammar-based fuzzing.

## Overview
[Luigi](https://github.com/spotify/luigi)-powered automation pipeline that:

1. Runs the [Tribble](https://projects.cispa.saarland/havrikov/tribble) fuzzer in transformation mode to transform a corpus of input grammars into restructured variants
2. Runs the tribble fuzzer in generation mode to generate inputs using the transformed grammars
3. Invokes the test subjects with the generated inputs using the code-coverage-instrumented runners for them in the [Subjects](https://projects.cispa.saarland/havrikov/subjects/) driver collection
4. Calculates conventional coverage metrics, such as median code coverage
5. Repeats the pipeline whilst skipping step 1. in order to obtain baseline coverage metrics for statistical significance assessment

## Running the Pipeline
Given the local presence of sources for the [Tribble](https://projects.cispa.saarland/havrikov/tribble) and [Subjects](https://projects.cispa.saarland/havrikov/subjects/) projects in their parent directory, `tool_dir`, the user must additionally chose a working directory, `experiment_dir`.

Furthermore, the user has to chose between using a local scheduler, recommended only for development purposes, and the [central scheduler](https://luigi.readthedocs.io/en/stable/central_scheduler.html). Central scheduling is used by default, demanding a running instance of the [luigid server](https://luigi.readthedocs.io/en/stable/central_scheduler.html#the-luigid-server), which can be started using the command `luigid`. Run observation is then possible via its web interface, which is reachable on port `8082` unless otherwise specified. Set the flag `local_scheduler` to use the local scheduler instead.

These options may be provided either via the command line interface or set in the `luigi.cfg` configuration file, with command line argument passing being the recommended option. Use the `--help` option to inform yourself about other options not listed above. Prominently, the user may supply a `grammar_transformation_mode` or `input_generation_mode` of their choosing, overriding the defaults encoded in the `luigi.cfg` configuration file.

The project can then be invoked via the command line, e.g.:

`python proof-of-concept.py --workers <num-of-CPUs> [other options]`

To get more information, refer to the [luigi](https://github.com/spotify/luigi)-powered documentation, in particular on [running luigi](https://luigi.readthedocs.io/en/stable/running_luigi.html).
