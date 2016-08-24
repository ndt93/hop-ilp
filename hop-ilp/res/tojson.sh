#!/usr/bin/env bash

PARSER_JAR="../parser/out/artifacts/parser_jar/parser.jar"

if [ $1 ]; then
    java -jar $PARSER_JAR $1 ./json
else
    for f in ./spudd/*.spudd; do
        java -jar $PARSER_JAR $f ./json
    done
fi
