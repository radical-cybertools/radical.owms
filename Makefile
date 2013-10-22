
.PHONY: all docs clean

all: docs


docs:
	make -C docs html
	@true


tests:
	python tests/run_tests.py tests/config/*cfg


copyright:
	@echo 'make it yourself!'


pylint:
	@rm -f pylint.out ;\
	for f in `find troy -name \*.py`; do \
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


viz:
	gource -s 0.1 -i 0 --title troy --max-files 99999 --max-file-lag -1 --user-friction 0.3 --user-scale 0.5 --camera-mode overview --highlight-users --hide progress,filenames -r 25 -viewport 1024x1024


clean:
	-rm -rf build/ troy.egg-info/ temp/ MANIFEST dist/ troy.egg-info pylint.out
	-find . -name \*.pyc -exec rm -f {} \;
	-make -C docs clean


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
# 	git  ci -m 'regenerate documentation'
# 	git co gh-pages
# 	git rebase devel
# 	git co devel
# 	git push --all
# 
