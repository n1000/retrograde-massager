/*
 * Copyright (c) 2022 Nathaniel Houghton <nathan@brainwerk.org>
 *
 * Permission to use, copy, modify, and distribute this software for
 * any purpose with or without fee is hereby granted, provided that
 * the above copyright notice and this permission notice appear in all
 * copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
 * WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
 * AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
 * DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA
 * OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
 * TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 * PERFORMANCE OF THIS SOFTWARE.
 */

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "retrogrades_data.h"

/*
 * This is just a binary search, and when an exact match is not found, it
 * returns the data before the insertion point index.
 *
 * A return value of 0 indicates that the retrograde data was found.
 */
int get_retrograde_bmap(uint64_t utc_ts, uint16_t *out)
{
    size_t min = 0, max = NUM_RETROGRADE_DATA_ENTRIES;
    size_t cur = 0;

    while (min < max) {
        cur = (min + max) / 2;

        assert(cur < NUM_RETROGRADE_DATA_ENTRIES);

        if (retrograde_data[cur].utc_timestamp > utc_ts) {
            max = cur;
        } else if (retrograde_data[cur].utc_timestamp < utc_ts) {
            min = cur + 1;
        } else {
            /* exact match */
            *out = retrograde_data[cur].retrograde_bmap;
            return 0;
        }
    }

    /*
     * Wasn't found, return max, which should be the position after the input
     * timestamp.
     */
    if (max > 0 && max < NUM_RETROGRADE_DATA_ENTRIES) {
        assert(retrograde_data[max - 1].utc_timestamp <= utc_ts);
        assert(retrograde_data[max].utc_timestamp >= utc_ts);

        *out = retrograde_data[max - 1].retrograde_bmap;
        return 0;
    } else {
        return -1;
    }
}

void display_retrograde_data(uint64_t ts, uint16_t data)
{
    uint32_t i;

    printf("ts: %lu\n", ts);

    for (i = 0; i < NUM_CELESTIAL_BODIES; ++i) {
        if (data & (1 << i)) {
            printf("\t%s\n", celestial_body_name[i]);
        }
    }
}

int main(int argc, char **argv)
{
    int i;

    for (i = 1; i < argc; ++i) {
        uint64_t in = strtoull(argv[i], NULL, 10);
        uint16_t out;

        int r = get_retrograde_bmap(in, &out);
        if (r == 0) {
            display_retrograde_data(in, out);
        } else {
            printf("%lu: failed to find retrograde data\n", in);
        }
    }

    return 0;
}
