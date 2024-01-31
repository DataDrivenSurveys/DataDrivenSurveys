#!/usr/bin/make -f
include makevars
package := ddsurveys
sources := $(wildcard $(package)/*.py)

# Help
help:
	@echo "    help"
	@echo "        Print this help message."
	@echo "    build"
	@echo "        Builds the wheel."
	@echo "    clean"
	@echo "        Remove build artifacts."
	@echo "    install"
	@echo "        If a wheel has been built then it is installed."
	@echo "    build-install"
	@echo "        Builds a wheel and then installs it."
	@echo "    test"
	@echo "        Run the project tests."
	@echo "    coverage"
	@echo "        Run tests and generate the coverage report."
	@echo "    coverage-report"
	@echo "        Open the coverage report html file."
	@echo "    cythonize"
	@echo "        Cythonize all files that are set as cythonizeable."
	@echo "    wheel"
	@echo "        An alias for calling make with the 'build' target."
	@echo "    stub"
	@echo "        Generate stub .pyi files inplace next to the original .py files."

# .PHONY goes here so that make without arguments prints help
.PHONY: help build clean install build-install test cythonize wheel coverage coverage-report stub dockerize-dev

build:
	@python3 setup.py build bdist_wheel
clean:
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
install:
	@pip3 install .
build-install: build install
test:
	@python3 ./setup.py nosetests
test-tox:
	@python3 ./setup.py tox
coverage: test
	@coverage html
	@open htmlcov/index.html
coverage-report:
	@open hmtlcov/index.html
cythonize:
	@python3 setup.py build_ext --inplace
wheel: build
stub: $(sources)
	stubgen --output . --package $(package)
dockerize-dev:
	docker-compose -f ./docker-compose.dev.yml up
