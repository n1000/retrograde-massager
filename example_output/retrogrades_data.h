#include <stdint.h>
#include <stddef.h>

#define NUM_CELESTIAL_BODIES 9

#define BITPOS_MERCURY 0
#define BITPOS_VENUS 1
#define BITPOS_MARS 2
#define BITPOS_JUPITER 3
#define BITPOS_SATURN 4
#define BITPOS_URANUS 5
#define BITPOS_NEPTUNE 6
#define BITPOS_PLUTO 7
#define BITPOS_MOON 8

#define MERCURY_BIT (1 << BITPOS_MERCURY)
#define VENUS_BIT (1 << BITPOS_VENUS)
#define MARS_BIT (1 << BITPOS_MARS)
#define JUPITER_BIT (1 << BITPOS_JUPITER)
#define SATURN_BIT (1 << BITPOS_SATURN)
#define URANUS_BIT (1 << BITPOS_URANUS)
#define NEPTUNE_BIT (1 << BITPOS_NEPTUNE)
#define PLUTO_BIT (1 << BITPOS_PLUTO)
#define MOON_BIT (1 << BITPOS_MOON)

struct retrograde_entry {
    uint64_t utc_timestamp;
    uint16_t retrograde_bmap;
};

extern const char *celestial_body_name[NUM_CELESTIAL_BODIES];
extern struct retrograde_entry retrograde_data[];
extern const size_t NUM_RETROGRADE_DATA_ENTRIES;
