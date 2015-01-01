.PHONY: all flake doc test cov
all: flake doc cov

doc:
	make -C docs html

flake:
	flake8 aiogibson tests

test: flake
	nosetests -s $(FLAGS) ./tests/

cov cover coverage:
	nosetests -s --with-cover --cover-html --cover-branches $(FLAGS) --cover-package aiogibson ./tests/
	@echo "open file://`pwd`/cover/index.html"

clean:
	find . -name __pycache__ |xargs rm -rf
	find . -type f -name '*.py[co]' -delete
	find . -type f -name '*~' -delete
	find . -type f -name '.*~' -delete
	find . -type f -name '@*' -delete
	find . -type f -name '#*#' -delete
	find . -type f -name '*.orig' -delete
	find . -type f -name '*.rej' -delete
	rm -f .coverage
	rm -rf coverage
	rm -rf docs/_build
