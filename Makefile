
.PHONY: all docs clean

PROJECT = owms
VERSION = $(shell git describe --tags --always)
FILES   = LICENSE.md MANIFEST.in README.md setup.py VERSION
DIRS    = owms examples docs tests

all: docs



sdist:
	python setup.py sdist

upload:
	python setup.py sdist upload

docs:
	echo "make documentation"
	make -C docs html
	
	echo "make tutorial tarball"
	cd         tutorial                                                           ; \
    rm -f      radical_owms_tutorial_examples.tgz                                 ; \
    rm -rf     radical_owms_tutorial_examples/                                    ; \
    mkdir      radical_owms_tutorial_examples/                                    ; \
    mkdir      radical_owms_tutorial_examples/input/                              ; \
    cp input/* radical_owms_tutorial_examples/input/                              ; \
    cp *.py    radical_owms_tutorial_examples/                                    ; \
    cp *.json  radical_owms_tutorial_examples/                                    ; \
    tar zcvf   radical_owms_tutorial_examples.tgz radical_owms_tutorial_examples/ ; \
    rm -rf     radical_owms_tutorial_examples/


install:
	@yes | head -n 1 | pip uninstall radical.owms > /dev/null ; pip install . > /dev/null

test:
	python tests/run_tests.py tests/configs/*cfg

copyright:
	perl bin/fix_copyright.pl

pylint:
	@rm pylint.out ;\
	for f in `find radical/owms -name \*.py`; do \
		echo "checking $$f"; \
		( \
	    res=`pylint -r n -f text $$f 2>&1 | grep -e '^[FE]'` ;\
		  test -z "$$res" || ( \
		       echo '----------------------------------------------------------------------' ;\
		       echo $$f ;\
		       echo '----------------------------------------------------------------------' ;\
		  		 echo $$res | sed -e 's/ \([FEWRC]:\)/\n\1/g' ;\
		  		 echo \
		  ) \
		) | tee -a pylint.out; \
	done ; \
	test "`cat pylint.out | wc -c`" = 0 || false && rm -f pylint.out

release: clean
	@echo $(VERSION)
	@echo $(VERSION) > VERSION
	@tar zcvf $(PROJECT)-$(VERSION).tgz $(FILES) $(DIRS)


viz:
	gource -s 0.1 -i 0 --title radical.owms --max-files 99999 --max-file-lag -1 --user-friction 0.3 --user-scale 0.5 --camera-mode overview --highlight-users --hide progress,filenames -r 25 -viewport 1024x1024

clean:
	-rm -f pylint.out radical/owms/VERSION MANIFEST setup.cfg
	-rm -rf build/ radical.owms.egg-info/ temp/ dist/ release/
	make -C docs clean
	find . -name \*.pyc -exec rm -f {} \;
	find . -name .\*.swp -exec rm -f {} \;

# pages: gh-pages
# 
# gh-pages:
# 	make clean
# 	make docs
# 	git add -f docs/build/html/*
# 	git add -f docs/build/html/*/*
# 	git add -f docs/build/doctrees/*
# 	git add -f docs/build/doctrees/*/*
# 	git add -f docs/source/*
# 	git add -f docs/source/*/*
# 	git ci  -m 'regenerate documentation'
# 	git co gh-pages
# 	git git merge devel
# 	git co devel
# 	git push --all

