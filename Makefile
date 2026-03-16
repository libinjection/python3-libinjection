
all: build
#
#

build: upstream libinjection/libinjection_wrap.c
	python3 setup.py --verbose build_ext --inplace

install: build
	sudo python3 setup.py --verbose install

test-unit: build words.py
	python3 -m pytest test_driver.py -v

.PHONY: test
test: test-unit

.PHONY: speed
speed:
	./speedtest.py

upstream: 
	[ -d $@ ] || git clone --depth=1 https://github.com/libinjection/libinjection.git upstream

libinjection/libinjection.h libinjection/libinjection_sqli.h libinjection/libinjection_error.h \
libinjection/libinjection_xss.h libinjection/libinjection_html5.h: upstream
	cp -f upstream/src/libinjection*.h upstream/src/libinjection*.c libinjection/
	# Compatibility patches for SWIG wrapping: fix type mismatches and visibility.
	# These sed invocations are pattern-matched to avoid breaking unrelated code.
	#
	# Fix return type mismatch: h5_state_data uses injection_result_t in definition but int in declaration
	sed -i 's/^static int h5_state_data(/static injection_result_t h5_state_data(/' libinjection/libinjection_html5.c
	# Fix return type mismatch: libinjection_is_sqli declared as injection_result_t but defined as int
	sed -i 's/^int libinjection_is_sqli(/injection_result_t libinjection_is_sqli(/' libinjection/libinjection_sqli.c
	# Remove static from helper functions so SWIG can wrap and expose them to Python
	# (static functions in a header cannot be called from libinjection_wrap.c)
	sed -i 's/^static void libinjection_sqli_reset(/void libinjection_sqli_reset(/' libinjection/libinjection_sqli.h libinjection/libinjection_sqli.c
	sed -i ':a;N;$$!ba;s/static char\nlibinjection_sqli_lookup_word/char\nlibinjection_sqli_lookup_word/g' libinjection/libinjection_sqli.h libinjection/libinjection_sqli.c
	sed -i ':a;N;$$!ba;s/static int\nlibinjection_sqli_blacklist/int\nlibinjection_sqli_blacklist/g' libinjection/libinjection_sqli.h libinjection/libinjection_sqli.c
	sed -i ':a;N;$$!ba;s/static int\nlibinjection_sqli_not_whitelist/int\nlibinjection_sqli_not_whitelist/g' libinjection/libinjection_sqli.h libinjection/libinjection_sqli.c

words.py: Makefile json2python.py upstream
	python3 json2python.py < upstream/src/sqlparse_data.json > words.py


libinjection/libinjection_wrap.c: libinjection/libinjection.i libinjection/libinjection.h \
libinjection/libinjection_sqli.h libinjection/libinjection_error.h \
libinjection/libinjection_xss.h libinjection/libinjection_html5.h
	swig -version
	swig -python -builtin -Wall -Wextra \
	     -o libinjection/libinjection_wrap.c \
	     -outdir libinjection \
	     libinjection/libinjection.i


.PHONY: copy

libinjection.so: libinjection/libinjection_wrap.c
	gcc -std=c99 -Wall -Werror -fpic -c libinjection/libinjection_sqli.c
	gcc -std=c99 -Wall -Werror -fpic -c libinjection/libinjection_xss.c
	gcc -std=c99 -Wall -Werror -fpic -c libinjection/libinjection_html5.c
	gcc -dynamiclib -shared -o libinjection.so libinjection_sqli.o libinjection_xss.o libinjection_html5.o

clean:
	@rm -rf build dist upstream
	@rm -f *.pyc *~ *.so *.o
	@rm -f nosetests.xml
	@rm -f words.py
	@rm -f libinjection/*~ libinjection/*.pyc
	@rm -f libinjection/libinjection.h libinjection/libinjection_error.h libinjection/libinjection_sqli.h libinjection/libinjection_sqli.c libinjection/libinjection_sqli_data.h
	@rm -f libinjection/libinjection_html5.h libinjection/libinjection_html5.c libinjection/libinjection_xss.h libinjection/libinjection_xss.c
	@rm -f libinjection/libinjection_wrap.c libinjection/libinjection.py
