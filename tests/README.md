This library interacts with the API for DocumentCloud.  Running the test suite
against the live server provides many challenges - it is slow, will not work
without an internet connection, and could give false failures for intermitent
network failures.  To resolve these issues we use VCR.py
(https://github.com/kevin1024/vcrpy) to record the HTTP requests.  When new
HTTP requests are needed for the tests, they are recorded against a
localinstance of the server.  Then the tests can be run against the
pre-recorded responses, quickly and without interacting with any other
software.

To record the HTTP requests, you must have a local dev environment of Squarelet
and DocumentCloud running.  You can find instructions for those here:
https://github.com/MuckRock/squarelet and
https://github.com/MuckRock/DocumentCloud.  

You should create a test user locally, with the username `test-user` and password `test-password`.

There are some tests which require the access and refresh tokens to be expired.  To accomodate this, those tests are expected to be run with the local Squarelet instance configured with very short lifetimes for those tokens.  You should record the regular tests, change the settings, run the short tests, then change the settings back.  The settings to change are located in `config/settings/base.py` in the Squarelet code base.  Find the follow lines and uncomment the second two:

```
    # These are used for testing token expiration
    # "ACCESS_TOKEN_LIFETIME": timedelta(seconds=2),
    # "REFRESH_TOKEN_LIFETIME": timedelta(seconds=5),
```

There is a Makefile included to help run the tests.  The following commands are available:

`test-clean` - This will clean all of the pre-recorded requests for the non-short tests

`test-clean-short` - This will clean all of the pre-recorded requests for the short tests

`test-create` - This will clean the non-short tests and then run all of them and record the HTTP requests.

`test-create-short` - This will clean the short tests and then run all of them and record the HTTP requests.

`test` - run all tests using the pre-recorded HTTP requests.  If an HTTP request is missing, it will fail.

`test-dev` - run all tests using the pre-recorded HTTP requests.  If an HTTP request is missing, record it.

`tox` - run all tests under multiple Python versions using tox.

`coverage` - run as `make test`, except generate a coverage report as well.

`check` - Run `pylint`, `black`, and `isort` on all of the source files.

`ship` - Release a new version of the library on PyPI.

A normal workflow would be to use `test-create` to create the intial saved requests, or if you want to re-record all of them for some reason.  You would then change the short settings as described above, and run `test-create-short`.  Running `test` should now pass while making no actual HTTP requests.  If you add a new test with a new request, you can run `test-dev` to record just the new request while leaving the existing ones in place.  The saved requests should be checked in to git.

## Troubleshooting

### Token Errors 
If you receive a lot of errors that are 405's with E requests.exceptions.HTTPError: 405 Client Error: Method Not Allowed for url: https://dev.squarelet.com/api/token/
You need to change the BASE_URI and AUTH_URI to https. 

### SSL Errors
If you receive a bunch of 500/SSL errors when running the tests, it is likely that your local dev environment doesn't have access to the necessary certificates to authenticate with your local DocumentCloud environment. 
You can copy the .PEM/.CRT file that is inside the docker container to your local environment and pass this file in so make the SSL errors go away. 

To resolve this you will want to have your local DocumentCloud environment running, including the Django container. You can find the container ID of a running container by running 
```docker ps```

Then, to retrieve the certificate run:
```docker cp container_id_here:/etc/ssl/certs/ca-certificates.crt ~```
Substitute ~ with the location where you would like to copy the certificate file, as ~ is the home directory. 

You can then run the full test-suite by re-recording results  and passing in the necessary certificate like so:
```REQUESTS_CA_BUNDLE=/path/to/ca-certificates.crt make test-create```
/path/to should be replaced by the actual location. 

### Assertion Errors

If you get a failure for the contributor method, it is because you need to set a full name for the test user within Squarelet. 

If you receive the following failure:
```assert len(list(all_documents)) > len(list(my_documents.results))```
It is because you need to have another user created on your local dev environment on Squarelet, have them verified, and have them upload at least one document. 
This tests asserts that the total sum of documents in your local dev environment is larger than those owned by you. This wouldn't hold true if your test user was the only user who has uploaded a document. 

If you receive this similar assertion failure:
```assert len(all_projects.results) > len(my_projects.results)```
You will need to have that other user create a project as well. This is to pass this assertion. 
