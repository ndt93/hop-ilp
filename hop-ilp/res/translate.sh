#!/usr/bin/env bash

cd ../../rddlsim

./run rddl.translate.RDDL2Format ../hop-ilp/res/$1 ../hop-ilp/res/spudd spudd_sperseus
