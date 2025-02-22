---
layout: default
title: Running In CI
---

In the [previous page](local-development) we set up a simple test harness to work with developing an LLM prompt locally. Let's get the test in CI so we can see how are test work over time.

The reason we want to run in CI, is that we want to you statistical measurements in a clean environment. The number of runs to get satistical value will be longer in time than is practical to be exicuted in the local environment. We also want to make sure we are making apples to apples comparisons, and are not getting strange results because of an unchecked in file on a developers local machine. For example, if we run a test 10 times, we may or may not see failures due to the non-deterministic nature of LLMs. If we are continully running the tests

## persist results in ci

We are going to use Github Actions in this example, but you can use whatever CI tool you have available. 


Now let's update those test to make them useful in our CI environment. Firstly, we were hard coding the number of tries a test should run.
```python
# test_allocations.py
def test_allocations():
    tries = 10
```

We will often want to change this number when developing locally, but in CI we will most likely want to keep it consistent. Here we will use our test runner to help out with that:

```python
# test_allocations.py
def test_allocations():
    tries = Runner.sample_size(3)
```

When invoked, sample_size will return whatever number you invoked it with, defaulting to 1 if you have not supplied it an argument, however, if the environment variable `CAT_AI_SAMPLE_SIZE` is set, then that number will be returned instead. This allows you to set the `CAT_AI_SAMPLE_SIZE` in your CI pipeline and always get that many runs, regardless of what argument gets set in source control while developers are working locally.



Now that we will be running each test a consistent number of times, we will care less about each individual test run and more about the overall success rate of the particular test. It will be of particular interest to some stakeholders who have a threshold of success in mind for particular prompts.

