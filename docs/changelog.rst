Changelog
---------

3.0.4
~~~~~

* Bug fix

3.0.3
~~~~~

* Convert list passed in to `DocumentClient.list` `id__in` parameter to string automatically.

3.0.2
~~~~~

* Bug fix

3.0.1
~~~~~

* Validate add-on data using `fastjsonschema`.  This allows add-ons to set and use default values in their config.yaml files, which is very convenient for cron add-ons.

3.0.0
~~~~~

* Use version 2.0 of the DocumentCloud API

  DocumentCloud's API now uses cursor pagination instead of page number pagination.  This allows for more efficient paging deep into the results of an API call.  It also removes the need for a costly count of all the results.  This will improve the performance of many API calls to DocumentCloud.  The tradeoff is that you can no longer randomly access pages of result, instead needing to go through them one at a time.  You also do not get a full count of all results for most API calls (searches still return a full count).

  The major change for API users is there no longer being a `__len__` method implemented for `APIResults`.  You also cannot directly pass in a page number for list calls.  Iterating through results still works as before - the next page will be automatically fetched.


2.4.0
~~~~~

* Incorporate command line testing of Add-Ons into base Add-On class
* Add-On class can accept refresh tokens for longer running use

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
