
all: build
#
#

build: upstream libinjection/libinjection_wrap.c
	rm -f libinjection/libinjection.py
	python3 setup.py --verbose build_ext --inplace

install: build
	sudo python3 setup.py --verbose install

test-unit: build words.py
	cd /tmp && python3 -m pytest $(CURDIR)/test_driver.py -v

.PHONY: test
test: test-unit

.PHONY: speed
speed:
	./speedtest.py

upstream: 
	[ -d $@ ] || git clone --depth=1 https://github.com/libinjection/libinjection.git upstream

libinjection/libinjection.h libinjection/libinjection_sqli.h libinjection/libinjection_error.h: upstream
	cp -f upstream/src/libinjection*.h upstream/src/libinjection*.c libinjection/

words.py: Makefile json2python.py upstream
	python3 json2python.py < upstream/src/sqlparse_data.json > words.py


libinjection/libinjection_wrap.c: libinjection/libinjection.i libinjection/libinjection.h libinjection/libinjection_sqli.h libinjection/libinjection_error.h
	swig -version
	swig -python -builtin -Wall -Wextra libinjection/libinjection.i


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
