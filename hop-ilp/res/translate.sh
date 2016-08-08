#!/usr/bin/env bash

if [ ! -z $1 ]
then
    rm ./spudd/$1
fi

cd ../../rddlsim

./run rddl.translate.RDDL2Format ../hop-ilp/res/rddl ../hop-ilp/res/spudd spudd_sperseus
