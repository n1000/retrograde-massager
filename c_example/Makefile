CFLAGS=-Wall
LDFLAGS=
CC=gcc

GEN_SCRIPT=../retrograde_massager.py
JSON_FILE=../retrogrades.json
GENERATED_FILE_PREFIX=retrogrades_data
GENERATED_C_FILE=${GENERATED_FILE_PREFIX}.c
GENERATED_H_FILE=${GENERATED_FILE_PREFIX}.h

c_example: c_example.o ${GENERATED_FILE_PREFIX}.o
	${CC} -o ${@} ${^} ${LDFLAGS}

c_example.o: c_example.c ${GENERATED_FILE_PREFIX}.o

${GENERATED_FILE_PREFIX}.o: ${GENERATED_FILE_PREFIX}.c ${GENERATED_FILE_PREFIX}.h

.c.o:
	${CC} -c ${<} ${CFLAGS}

${GENERATED_FILE_PREFIX}%c ${GENERATED_FILE_PREFIX}%h: ${JSON_FILE}
	${GEN_SCRIPT} c ${^} ${GENERATED_FILE_PREFIX}

clean:
	rm -f c_example *.core *.o ${GENERATED_C_FILE} ${GENERATED_H_FILE}
