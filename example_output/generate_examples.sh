#!/bin/sh

JSON_FILE="../retrogrades.json"
OUTPUT_PREFIX="retrogrades_data"

if [ ! -f "${JSON_FILE}" ]; then
	printf "error: could not find input JSON file %s\n" "${JSON_FILE}" 2>&1
	exit 1
fi

rm -f "${OUTPUT_PREFIX}.db" &&
echo "Generating SQLite..." &&
../retrograde_massager.py sqlite ../retrogrades.json "${OUTPUT_PREFIX}" &&
echo "Generating SQLite db..." &&
sqlite3 "${OUTPUT_PREFIX}.db" < "${OUTPUT_PREFIX}.sqlite" &&
echo "Generating C..." &&
../retrograde_massager.py c ../retrogrades.json "${OUTPUT_PREFIX}" &&
echo success.
