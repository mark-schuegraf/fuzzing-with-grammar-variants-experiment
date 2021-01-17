# Grammar Transformations

Exploring how transforming grammars affects grammar-based fuzzing.

## Overview
[Luigi](https://github.com/spotify/luigi)-powered automation pipeline that:

1. Runs the [tribble](https://projects.cispa.saarland/havrikov/tribble) fuzzer in transformation mode to transform a corpus of input grammars into restructured variants
2. Runs the tribble fuzzer in generation mode to generate inputs using the transformed grammars
3. Invokes the test subjects with the generated inputs using the code-coverage-instrumented runners for them in the [subjects](https://projects.cispa.saarland/havrikov/subjects/) driver collection
4. Calculates conventional coverage metrics, such as median code coverage
5. Repeats the pipeline whilst skipping step 1. in order to obtain baseline coverage metrics for statistical significance assessment
