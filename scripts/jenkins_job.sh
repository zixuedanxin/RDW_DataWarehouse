#!/bin/bash

# temporay hardcode python3, it should use virtualenv python3
export PATH=/usr/local/bin/:$PATH


# run the py.test --pep8
cd .. 
find . -type f |grep ".py$" | xargs  py.test --pep8
# run rhino jslint

# run unit test
