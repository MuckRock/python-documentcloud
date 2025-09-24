
# remove the pre-recorded HTTP requests for normal tests
test-clean:
	rm -rf tests/cassettes/test_*/*
	rm -rf tests/cassettes/fixtures/*

# remove the pre-recorded HTTP requests for short tests
# short tests have the server set to expire access tokens quickly in order to
# test behavior around expired tokens
test-clean-short:
	rm -rf tests/cassettes/short_fixtures/*

# run normal tests and record all HTTP requests
test-create: test-clean
	pytest --record-mode=all -m "not short"

# run short tests and record all HTTP requests
test-create-short: test-clean-short
	pytest --record-mode=all -m "short"

# run all tests using the pre-recorded HTTP requests - will fail on missing request
test:
	pytest --record-mode=none --block-network -vv

# run tests using pre-recorded HTTP requets if they exist, and recording them if missing
test-dev:
	pytest --record-mode=new_episodes

# run tests under python2 and python3
tox:
	tox

# run tests using pre-recorded HTTP requests and create a coverage report
coverage:
	coverage erase
	coverage run --source documentcloud -m py.test --record-mode=none --block-network
	coverage html
	coverage report -m

# ensure all code is linted, formatted and import are sorted
check:
	pylint documentcloud
	black documentcloud
	isort -rc documentcloud
	pylint tests
	black tests
	isort -rc tests

# release a new version of the package to PyPI
ship:
	rm -rf build/
	python setup.py sdist bdist_wheel
	twine upload dist/* --skip-existing
