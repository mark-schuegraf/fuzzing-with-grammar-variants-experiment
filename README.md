# Grammar Transformations

Exploring how transforming grammars affects grammar-based fuzzing.

## Overview
[Luigi](https://github.com/spotify/luigi)-powered automation pipeline that:

1. Runs the [tribble](https://projects.cispa.saarland/havrikov/tribble) fuzzer in transformation mode to transform a corpus of input grammars into restructured variants
2. Runs the tribble fuzzer in generation mode to generate inputs using the transformed grammars
3. Invokes the test subjects with the generated inputs using the code-coverage-instrumented runners for them in the [subjects](https://projects.cispa.saarland/havrikov/subjects/) driver collection
4. Calculates conventional coverage metrics, such as median code coverage
5. Repeats the pipeline whilst skipping step 1. in order to obtain baseline coverage metrics for statistical significance assessment

## Running the Pipeline
Given the local presence of sources for the [tribble](https://projects.cispa.saarland/havrikov/tribble) and [subjects](https://projects.cispa.saarland/havrikov/subjects/) projects in their parent directory, `tool_dir`, the user must additionally chose a working directory, `experiment_dir`, and provide both in the experiment configuration file, `luigi.cfg`. Therein, amongst other things, options pertaining to the mode of grammar transformation and input generation may be adjusted as well.

Importantly, the user has to chose between using a local scheduler, recommended only for development purposes, and the [central scheduler](https://luigi.readthedocs.io/en/stable/central_scheduler.html). To enable local scheduling, set `local_scheduler = True` in the configuration file. To use central scheduling instead, set `local_scheduler = False` and start the [luigi deamon](https://luigi.readthedocs.io/en/stable/central_scheduler.html#the-luigid-server) using `luigid`. Run observation is then possible via its web interface, which is reachable on port `8082` unless otherwise specified in `luigi.cfg`.

The project can then be invoked via the command-line, e.g.:

`python proof-of-concept.py --workers <num-of-CPUs>`
 
To get more information, refer to the [luigi](https://github.com/spotify/luigi)-powered documentation, in particular on [running luigi](https://luigi.readthedocs.io/en/stable/running_luigi.html).
