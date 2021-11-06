# Grammar Transformations

Experiment exploring how grammar transformations affect fuzzing performance in the context of various fuzzing strategies and subjects.

## Overview
[Luigi](https://github.com/spotify/luigi)-powered automation pipeline that:

1. Runs the [havrikov/tribble](https://projects.cispa.saarland/havrikov/tribble) fuzzer in transformation mode to transform a corpus of input grammars into restructured variants
2. Runs the tribble fuzzer in generation mode to generate inputs using the transformed grammars
3. Invokes the test subjects with the generated inputs using the code-coverage-instrumented runners for them in the [havrikov/text-processing-java-projects](https://github.com/havrikov/text-processing-java-projects) driver collection
4. Produces statistical reports for each configuration detailing differences in code coverage and code coverage growth rate, as well as their significance measured using the [Wilcoxon signed-rank test](https://en.m.wikipedia.org/wiki/Wilcoxon_signed-rank_test)
5. Renders the results into a [Jupyter notebook](https://jupyter.org/) using [pandas](https://pandas.pydata.org/) to display statistical reports as tables and [seaborn](https://seaborn.pydata.org/) to plot coverage progression. Note that it may take quite long to render all coverage progression plots. Prerendered plots can therefore also be found at [mark-schuegraf/fuzzing-with-grammar-variants-results](https://github.com/mark-schuegraf/fuzzing-with-grammar-variants-results)

## Configuration

The pipeline may be configured by modifying the luigi configuration file `luigi.cfg` that already makes use of some of [the available configuration options](https://github.com/spotify/luigi/blob/master/doc/configuration.rst).

Additional parametrization is done via the command line. To change command line arguments, modify `run_experiments.sh` and `start_luigi_daemon.sh` accordingly.

Notable parameters not detailed in the luigi documentation are:
1. `--only-transformation=<NAME>` that allows running the pipeline only for one particular transformation
2. `--only-language=<NAME>` that allows running the pipeline only for one particular language
3. `--enable-plotting=True` (default is `False`) that enables rendering coverage scatter plots to file as part of the experiment, rather than inline in the Jupyter notebook afterwards

Finally, the pipeline requires the input grammar directory `$EXPERIMENT_DIR/grammars` to exist. Before running the pipeline, it is necessary to populate it with the grammars to be tested. These can be found in `grammars/in-use`. It is also possible to swap these grammars out for others from `grammars/candidates` or elsewhere, but then corresponding entries need to be added to `lib/parametrization.py`.

## Running the Pipeline

1. Install Java 11
2. Pull the `master` branch of the transformation-mode-enhanced fork of the [havrikov/tribble](https://github.com/havrikov/tribble) fuzzer: [mark-schuegraf/tribble](https://github.com/mark-schuegraf/tribble) and the `master` branch of [havrikov/text-processing-java-projects](https://github.com/havrikov/text-processing-java-projects)
3. Build the projects using `./gradlew build`
4. Install python 3.8, for example using [pyenv](https://github.com/pyenv/pyenv)
5. Install [pipenv](https://pipenv.pypa.io/)
6. Install pipenv dependencies specified in the `Pipfile` using `pipenv install`
7. Load the virtual pipenv environment by invoking `pipenv shell`
8. Run the pipeline using `./run_experiments.sh`
9. (Optional) Monitor the experiment using the web interface of the [luigi centralized scheduler](https://luigi.readthedocs.io/en/stable/central_scheduler.html) available at `http://localhost:9009`

## Troubleshooting

In rare cases, tribble generation may fail with the exception: `java.lang.IllegalArgumentException: loops not allowed`

However, this does not mean that the input grammar contains loops. Rather, they may be created during the contraction hierarchy precomputation step required by contraction-hierarchy-based shortest path algorithms. Since such an algorithm is in use by tribble for reasons of efficiency, there is the risk of that exception being thrown.

To deal with this issue, first run the pipeline using the regular tribble JAR. Then, delete the JAR living at `$EXPERIMENT_DIR/tools/build/tribble.jar` and before running the pipeline again, pull the `tribble/loop-fix-dijkstra` branch.  Then run the pipeline again. The missing inputs will then be generated using a version of tribble that employs Dijkstra to compute shortest paths instead, which has no precomputation step and thus does not produce self-loops in those fringe cases.
