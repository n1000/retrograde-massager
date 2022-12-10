#!/bin/env python3
#
# Copyright (c) 2022 Nathaniel Houghton <nathan@brainwerk.org>
#
# Permission to use, copy, modify, and distribute this software for
# any purpose with or without fee is hereby granted, provided that
# the above copyright notice and this permission notice appear in all
# copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA
# OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#

import argparse
import json
from datetime import datetime, timezone

# Input data is a dict containing { "name": bool, ... } info.
#
# Returns a { "name": bit_pos, ... }  dictionary
def gen_name_bitpos_map(data):
    name_to_bitmap_pos = {}

    for idx, name in enumerate(data):
        name_to_bitmap_pos[name] = idx

    return name_to_bitmap_pos

def print_c_file(f, header_filename, data_rows, name_to_bitpos_map):
    sorted_name_bit_tuple_list = sorted(list(name_to_bitpos_map.items()), key=lambda x: x[1])
    sorted_name_list = [x[0] for x in sorted_name_bit_tuple_list]

    print("#include \"{}\"".format(header_filename), file=f)
    print(file=f)

    celest_body_list = ", ".join(["\"{}\"".format(x) for x in sorted_name_list])
    print("const char *celestial_body_name[] = {{ {} }};".format(celest_body_list), file=f)

    print(file=f)

    print("struct retrograde_entry retrograde_data[] = {", file=f)

    for (date_ts, bmap) in data_rows:
        print("    {", end="", file=f)
        print(" {}, 0x{:04x} ".format(date_ts, bmap), end="", file=f)
        print("},", file=f)

    print("};", file=f)

    print(file=f)

    print("const size_t NUM_RETROGRADE_DATA_ENTRIES = sizeof(retrograde_data) / sizeof(retrograde_data[0]);", file=f)

def print_c_header(f, name_to_bitpos_map):
    sorted_name_bit_tuple_list = sorted(list(name_to_bitpos_map.items()), key=lambda x: x[1])
    sorted_name_list = [x[0] for x in sorted_name_bit_tuple_list]

    print("#include <stdint.h>", file=f)
    print("#include <stddef.h>", file=f)
    print(file=f)

    print("#define NUM_CELESTIAL_BODIES {}".format(len(name_to_bitpos_map)), file=f)
    print(file=f)

    for planet, bitpos in name_to_bitpos_map.items():
        print("#define BITPOS_{} {}".format(planet.upper(), bitpos), file=f)

    print(file=f)

    for planet, bitpos in name_to_bitpos_map.items():
        print("#define {}_BIT (1 << BITPOS_{})".format(planet.upper(), planet.upper()), file=f)

    print(file=f)

    print("struct retrograde_entry {", file=f)
    print("    uint64_t utc_timestamp;", file=f)
    print("    uint16_t retrograde_bmap;", file=f)
    print("};", file=f)

    print(file=f)

    print("extern const char *celestial_body_name[NUM_CELESTIAL_BODIES];", file=f)
    print("extern struct retrograde_entry retrograde_data[];", file=f)
    print("extern const size_t NUM_RETROGRADE_DATA_ENTRIES;", file=f)

def make_bitmap(name_to_bitpos_map, data):
    bitmap = 0

    for planet, bitpos in name_to_bitpos_map.items():
        if data[planet]:
            bitmap |= (1 << bitpos)

    return bitmap

# output is a list of (date, bitmap) tuples
def extract_json_data(input_filename):
    output_rows = []
    name_to_bitpos_map = {}

    first_row = True
    prev_data = None
    with open(input_filename) as f:
        j = json.load(f)

        for date_str, data in j["dates"].items():
            if first_row:
                # assume that every entry lists all the planets
                name_to_bitpos_map = gen_name_bitpos_map(data)
                first_row = False

            if prev_data is None or prev_data != data:
                date = datetime.strptime("{}+0000".format(date_str), '%Y-%m-%d%z')
                timestamp = int(date.timestamp())
                bitmap = make_bitmap(name_to_bitpos_map, data)
                output_rows.append((timestamp, bitmap))
                prev_data = data

    return output_rows, name_to_bitpos_map

def gen_c_output(args, name_to_bitpos_map, data_rows):
    output_c_filename = "{}.c".format(args.output_file_prefix)
    output_h_filename = "{}.h".format(args.output_file_prefix)

    with open(output_h_filename, "w") as f:
        print_c_header(f, name_to_bitpos_map)

    print("Generated {}.".format(output_h_filename))

    with open(output_c_filename, "w") as f:
        print_c_file(f, output_h_filename, data_rows, name_to_bitpos_map)

    print("Generated {}.".format(output_c_filename))

def gen_sqlite_output(args, name_to_bitpos_map, data_rows):
    output_filename = "{}.sqlite".format(args.output_file_prefix)

    with open(output_filename, "w") as f:
        print("CREATE TABLE IF NOT EXISTS retrograde_table (", file=f)
        print("    timestamp_seconds_utc INTEGER PRIMARY KEY", file=f)

        for planet, bitpos in name_to_bitpos_map.items():
            print(",    {} INTEGER".format(planet), file=f)

        print(");", file=f);

        print(file=f)

        for (date_ts, bmap) in data_rows:
            column_value_list = [("timestamp_seconds_utc", date_ts)]
            for name, bit_idx in name_to_bitpos_map.items():
                if (1 << bit_idx) & bmap:
                    val = 1
                else:
                    val = 0

                column_value_list.append((name, val))

            if column_value_list:
                print("INSERT INTO retrograde_table ({}) VALUES({});".format(
                    ", ".join([str(x[0]) for x in column_value_list]),
                    ", ".join([str(x[1]) for x in column_value_list])),
                    file=f)

    print("Generated {}.".format(output_filename))

def main():
    # Celestial body to bit mapping
    #
    # { "name": bit_pos, ... }
    name_to_bitmap_pos = {}

    parser = argparse.ArgumentParser(prog="retrograde_massager", description="Massages retrograde json data files into other formats")

    parser.add_argument("output_mode", choices=["c", "sqlite"])
    parser.add_argument("input_json_file")
    parser.add_argument("output_file_prefix")

    args = parser.parse_args()

    extracted_data, name_to_bitpos_map = extract_json_data(args.input_json_file)

    if args.output_mode == "c":
        gen_c_output(args, name_to_bitpos_map, extracted_data)
    elif args.output_mode == "sqlite":
        gen_sqlite_output(args, name_to_bitpos_map, extracted_data)

if __name__ == "__main__":
    main()
