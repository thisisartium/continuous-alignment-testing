[![Python Tests][python-tests-badge]][python-tests-link]
[![CAT][cat-badge]][cat-link]
# Continuous Alignment Testing (CAT) Framework
A framework for implementing Continuous Alignment Testing (CAT) for LLM-based applications.
## Overview
CAT provides the infrastructure to:
- Run and track automated tests against an AI application.
- Store and analyze AI test results over iterations.
- Monitor reliability changes in an AI application as prompts, models, code, and data evolve.
- Integrate AI tests into the CI pipeline.
- Build the AI application as an API service using Python and use any language to invoke it.
- Ensure AI applications are reliable while maintaining creativity.
- Iterate on prompts and code while measuring improvements.
  
## Example Apps

- [team_recommender - Team Recommender](examples/team_recommender/readme.md)
- you next idea?
  
## Documentation
[Github Pages][github-pages-index]

Edit Pages in [docs](docs) and deploy using CI: [![github-pages-badge]][github-pages-deploy-link]

## Wiki
[Wiki Pages][wiki]

[python-tests-badge]: https://github.com/thisisartium/continuous-alignment-testing/actions/workflows/python-tests.yml/badge.svg
[python-tests-link]: https://github.com/thisisartium/continuous-alignment-testing/actions/workflows/python-tests.yml
[cat-badge]: https://github.com/thisisartium/continuous-alignment-testing/actions/workflows/cat-test-examples.yml/badge.svg
[cat-link]: https://github.com/thisisartium/continuous-alignment-testing/actions/workflows/cat-test-examples.yml
[wiki]: https://github.com/thisisartium/continuous-alignment-testing/wiki
[github-pages-index]: https://thisisartium.github.io/continuous-alignment-testing/
[github-pages-source]: https://github.com/thisisartium/continuous-alignment-testing/tree/main/docs
[github-pages-badge]: https://github.com/thisisartium/continuous-alignment-testing/actions/workflows/pages/pages-build-deployment/badge.svg
[github-pages-deploy-link]: https://github.com/thisisartium/continuous-alignment-testing/actions/workflows/pages/pages-build-deployment
