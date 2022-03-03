Changelog
---------

2.3.2
~~~~~

* Fix `CronAddOn`

2.3.1
~~~~~

* Fix `rate_limit_sleep` call

2.3.0
~~~~~

* Add Add-On module
* Add a `rate_limit_sleep` option to the base client


2.2.1
~~~~~

* Fix installation instructions


2.2.0
~~~~~

* Add an extension paramater to upload_directory


2.1.4
~~~~~

* Add publish_at field to Document

2.1.3
~~~~~

* Re-add support for the mentions parameter

2.1.2
~~~~~

* Update base URL from api.beta.documentcloud.org to api.www.documentcloud.org

2.1.1
~~~~~

* Added original_extension field to Document
* Properly send authentication when fetching private assets

2.1.0
~~~~~

* Add a process method to document

2.0.2
~~~~~

* Add logging and error handling to upload_directory 
* Add request retry logic for PUT requests to S3 and to file fetching requests
* Respect bulk limit for adding documents to a project

2.0.1
~~~~~

* Add long description to PyPI
* More complete documentation

2.0.0
~~~~~

* Initial release of re-written library for the new DocumentCloud API
