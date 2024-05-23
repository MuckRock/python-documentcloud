Changelog
---------

4.1.3
~~~~~
* Fix DELETE URL for documents

4.1.1
~~~~~
* Refresh tokens on 429 response codes

4.1.0
~~~~~
* Add `revision_control` as an allowed upload parameter.

4.0.1
~~~~~
* Reformats some strings in tests to conform to pylint standards.


4.0.0
~~~~~
* Removes support for Python2


3.8.0
~~~~~
* Add `charge_credits` to `AddOn`


3.7.1
~~~~~
* Fixes an indentation bug present in 3.7.0


3.7.0
~~~~~

* Add `clear_documents` and `add_documents` to `Project`.
* Use these new methods to fix altering a `Project`'s document list and saving it, preventing succesive API calls from over writing each other.


3.6.0
~~~~~

* Added upload_urls() to documents, which allows you to upload a list of URLs via a bulk API call, instead of just one at a time. 


3.5.0
~~~~~

* Added get_errors() to documents, which allows you to see errors for particular documents. 

3.4.0
~~~~~

* Improved upload_directory() to handle uploading directories containing all supported file types

3.3.9
~~~~~

* Make APIResults iteration non-recursive to avoid maximum rescursion limit errors

3.3.8
~~~~~

* Support for soft time out caching

3.3.7
~~~~~

* Fix bug with document text files decoding

3.3.6
~~~~~

* Fix bug when re-running Add-On with selected documents

3.3.5
~~~~~

* Fix bug of child client's not properly setting the parent attribute after
  paginating past the first page

3.3.4
~~~~~

* Refactor `rerun_addon` to allow including the current document in the next run

3.3.3
~~~~~

* Fix bug in `AddOn.get_documents` if no documents are passed in

3.3.2
~~~~~

* Fix bug in soft time out rerunning

3.3.1
~~~~~

* Soft time out scales better

3.3.0
~~~~~

* Support v2 configuration for passing more than 10 properties into an add-on

3.2.1
~~~~~

* `SoftTimeOutAddOn` class dismisses current run after creating a new run

3.2.0
~~~~~

* Add `SoftTimeOutAddOn` class
* Have `AddOn` methods which require an ID print debug information when ID is
  missing instead of doing nothing

3.1.4
~~~~~

* Add method `get_page_position_json_url` to `Document`

3.1.3
~~~~~

* Add method `get_document_count` to `AddOn`

3.1.2
~~~~~

* Add support for setting `delayed_index`

3.1.0
~~~~~

* Add `get_documents` method to `AddOn` for iterating over documents from either a selection or query

3.0.6
~~~~~

* Add support for event add-ons

3.0.5
~~~~~

* Fix issue with Add-On upload_file when uploading binary files

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
