Documents
=========

Methods for drawing down, editing and uploading data about documents.

DocumentClient
--------------

.. class:: documentcloud.documents.DocumentClient

   The document client gives access to retrieval and uploading of documents.
   It is generally accessed as ``client.documents``.


   .. method:: all(self, **params)

       An alias for :meth:`list`.


   .. method:: get(id_, expand=None)

      Return the document with the provided DocumentCloud identifer. ::

           >>> from documentcloud import DocumentCloud
           >>> client = DocumentCloud(USERNAME, PASSWORD)
           >>> client.documents.get(71072)
           <Document: Final OIR Report>

      The identifier may be just the numeric ID (71072, preferred), the old style ID-slug
      (71072-oir-final-report), or the new style slug-id (oir-final-report-71072).

      Setting expand allows for the user or organization details to be fetched with the
      document, instead of requiring a separate API request to fetch them.  Set expand to
      a list of the values you would like expanded. ::

           >>> client.documents.get(71072, expand=["user"])
           >>> client.documents.get(71072, expand=["user", "organization"])


   .. method:: list(self, **params)

      Return a list of all documents, possibly filtered by the given parameters.
      Please see the full `API documentation`_ for available parameters.


   .. method:: search(query, **params)
      
      Return a list of documents that match the provided query. ::
      
      >>> from documentcloud import DocumentCloud
      >>> client = DocumentCloud()
      >>> obj_list = client.documents.search('Ruben Salazar')
      >>> obj_list[0]
      <Document: Final OIR Report>

      The params may be set to any parameters that the search end point takes.
      Please see the full `search documentation`_ for query syntax and available
      parameters.


   .. method:: upload(pdf, **kwargs)

      Upload a PDF to DocumentCloud. You must be authorized to do this. Returns
      the object representing the new record you've created. You can submit either
      a file path or a file object.

      >>> from documentcloud import DocumentCloud
      >>> client = DocumentCloud(USERNAME, PASSWORD)
      >>> new_id = client.documents.upload("/home/ben/test.pdf", title="Test PDF")
      >>> # Now fetch it
      >>> client.documents.get(new_id)
      <Document: Test PDF>

      You can also use URLs which link to PDFs, if that's the kind of thing you
      want to do.

      >>> upload("http://ord.legistar.com/Chicago/attachments/e3a0cbcb-044d-4ec3-9848-23c5692b1943.pdf")

      You may set the ``kwargs`` to any of the writable attributes as
      described in :meth:`documentcloud.documents.Document.put`.
      Additionally, you may set ``force_ocr`` in order to force OCR to take
      place even if the document has embedded text. You may specify which
      OCR engine to use for OCR by setting ``ocr_engine`` to either ``tess4`` for tesseract
      or ``textract`` for Amazon Textract. 
      Note that Amazon Textract uses AI Credits and requires a DocumentCloud Premium account. 
      You may set ``project`` to the ID of a project to upload the document into, or
      ``projects``, a list of project IDs to upload the document into.
      If you are uploading a non-PDF document type, you must set
      ``original_extension`` to the extension of the file type, such as
      ``docx`` or ``jpg``.


   .. method:: upload_directory(path, handle_errors=False, extensions=".pdf" **kwargs)

      Searches through the provided path and attempts to upload all the PDFs it
      can find. Metadata, which accepts the same keywords as :meth:`upload`,
      provided to the other keyword arguments will be recorded for all uploads
      (except for title which will be set based on the filename). Returns a
      list of document objects that are created. Be warned, this will upload
      any documents in directories inside the path you specify.  The
      handle_errors parameter will catch and print errors generated by the
      network request or the DocumentCloud API, log them, and try to continue
      processing.  This might be useful if you are uploading a very large
      directory and do not want temporary network problems to stop the entire
      upload. By default, extensions is set to ".pdf", so it will only upload 
      PDFs in the specified directory. You can specify a different extension, 
      a list of extensions, or None. If None is explicitly specified, it will 
      upload any documents that are supported by DocumentCloud in the present directory. 
      If you pass a file extension type that is not supported by DocumentCloud, 
      ValueError will be raised telling you which extension is not supported. 
        
      The following will upload all PDFs in the groucho_marx directory: 
         >>> from documentcloud import DocumentCloud
         >>> client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)
         >>> obj_list = client.documents.upload_directory('/home/ben/pdfs/groucho_marx/')
    
      The following will upload all .txt and .jpg files in the groucho_marx directory: 
         >>> obj_list = client.documents.upload_directory('/home/ben/pdfs/groucho_marx/', extensions = ['.txt', '.jpg'])

      The following will upload all files that are supported by DocumentCloud in the groucho_marx directory:
         >>> obj_list = client.documents.upload_directory('/home/ben/pdfs/groucho_marx/', extensions=None)


   .. method:: upload_urls(self, url_list, handle_errors=False, **kwargs)
   
      Given a list of urls, it will attempt to upload the URLs in batches of 25 at a time. 

      >>> urls = ["https://www.chicago.gov/content/dam/city/depts/dcd/tif/22reports/T_072_24thMichiganAR22.pdf", "https://www.chicago.gov/content/dam/city/depts/dcd/tif/22reports/T_063_CanalCongressAR22.pdf"]
      >>> new = client.documents.upload_urls(urls)
      >>> new
      [<Document: 23932356 - T_072_24thMichiganAR22>, <Document: 23932357 - T_063_CanalCongressAR22>]



Document
--------

.. class:: documentcloud.documents.Document

   An individual document, as obtained by the :class:`documentcloud.documents.DocumentClient`.

   .. method:: put()

      Save changes to a document back to DocumentCloud. You must be authorized to
      make these changes. Only the
      :attr:`access`,
      :attr:`data`,
      :attr:`description`,
      :attr:`language`,
      :attr:`related_article`,
      :attr:`published_url`,
      :attr:`source`,
      and :attr:`title`,
      attributes may be edited. ::

           >>> # Grab a document
           >>> obj = client.documents.get('71072')
           >>> print(obj.title)
           Draft OIR Report
           >>> # Change its title
           >>> obj.title = "Brand new title"
           >>> print(obj.title)
           Brand New Title
           >>> # Save those changes
           >>> obj.put()

   .. method:: delete()

      Delete a document from DocumentCloud. You must be authorized to make these changes. ::

           >>> obj = client.documents.get('71072-oir-final-report')
           >>> obj.delete()

   .. method:: process()

       This will re-process the document.  Useful if there was an intermittent error.

   .. method:: save()

       An alias for :meth:`put` that saves changes back to DocumentCloud.


   .. attribute:: access

       The privacy level of the resource within the DocumentCloud system. It will
       be either ``public``, ``private`` or ``organization``, the last of which
       means the is only visible to members of the contributors organization. Can
       be edited and saved with a put command.

   .. attribute:: annotations

      A client to access and update the annotations on the document.  See
      :class:`Annotation` for more information.

   .. attribute:: asset_url

      The base URL to obtain the static assets for this document.  See the `API
      documentation`_ for more details.

   .. attribute:: canonical_url

       The URL where the document is hosted at documentcloud.org.

   .. attribute:: contributor

       The user who originally uploaded the document.

   .. attribute:: contributor_organization

       The organizational affiliation of the user who originally uploaded the document.
   
   .. attribute:: contributor_organization_slug

       The slug (url friendly identifier) of the organization that the user who originally uploaded the document belongs to. 

   .. attribute:: created_at

       The date and time that the document was created, in Python's datetime format.

   .. attribute:: data

       A dictionary containing supplementary data linked to the document. This can
       be any old thing. It's useful if you'd like to store additional metadata.
       Can be edited and saved with a put command.

           >>> obj = client.documents.get('83251-fbi-file-on-christopher-biggie-smalls-wallace')
           >>> obj.data
           {'category': 'hip-hop', 'byline': 'Ben Welsh', 'pub_date': datetime.date(2011, 3, 1)}

       Keys must be strings and only contain alphanumeric characters.

   .. attribute:: description

       A summary of the document. Can be edited and saved with a put command.

   .. attribute:: edit_access

      A boolean indicating whether or not you have the ability to save this
      document.

   .. attribute:: file_hash

       A hash representation of the raw PDF data as a hexadecimal string.

           >>> obj = client.documents.get('1021571-lafd-2013-hiring-statistics')
           >>> obj.file_hash
           '872b9b858f5f3e6bb6086fec7f05dd464b60eb26'

       You could recreate this hexadecimal hash yourself using the `SHA-1
       algorithm <https://en.wikipedia.org/wiki/SHA-1>`_.

           >>> import hashlib
           >>> hashlib.sha1(obj.pdf).hexdigest()
           '872b9b858f5f3e6bb6086fec7f05dd464b60eb26'

   .. attribute:: full_text

       Returns the full text of the document, as extracted from the original PDF
       by DocumentCloud. Results may vary, but this will give you what they got.

           >>> obj = client.documents.get('71072-oir-final-report')
           >>> obj.full_text
           "Review of the Los Angeles County Sheriff's\nDepartment's Investigation
           into the\nHomicide of Ruben Salazar\nA Special Report by the\nLos
           Angeles County Office of Independent Review\n ...

   .. attribute:: full_text_url

       Returns the URL that contains the full text of the document, as extracted
       from the original PDF by DocumentCloud.

   .. method:: get_errors()
      
      Returns a list containing entries for each error on the document. 

      >>> new = client.documents.upload("https://www.launchcamden.com/wp-content/uploads/2023/08/7.13.23_01002.pdf")
      >>> client.documents.get(new.id).get_errors()
      [{'id': 96136, 'created_at': datetime.datetime(2023, 8, 30, 16, 28, 8, 594859), 'message': '404 Client Error: Not Found for url: https://www.launchcamden.com/wp-content/uploads/2023/08/7.13.23_01002.pdf'}]

   .. method:: get_json_text()

       Returns the full text of the document, in a custom JSON format, indexed by page. May also be referenced shorthand as ``json_text``. Useful if trying to compare text throughout the document without making an API call to get the text of each page. Consult the full API documentation for more details. 

   .. method:: get_page_text(page)

       Submit a page number and receive the raw text extracted from it by DocumentCloud.

       >>> obj = client.documents.get('1088501-adventuretime-alta')
       >>> txt = obj.get_page_text(1)
       # Let's print just the first line
       >>> print(txt.split("\n")[0])
       STATE OF CALIFORNIA- HEALTH AND HUMAN SERVICES AGENCY
   
   .. method:: get_page_text_url(page)

       Retrieve the link to the static asset where the page's plaintext is available. If the document is public, the URL will point to S3, otherwise it will point to an internal DocumentCloud URL to verify that the user has permissions to view the page.

   .. method:: get_page_position_json(page)

       Submit a page number and receive the page text position information in
       JSON format

       >>> obj = client.documents.get('1088501-adventuretime-alta')
       >>> json = obj.get_page_position_json(1)

   .. method:: get_page_position_json_url(page)

       Submit a page number and receive a link to the static asset where page text position information is in JSON format. If the document is public, the URL will point to S3, otherwise it will point to an internal DocumentCloud URL to verify that the user has permissions to view the page.

   .. attribute:: id

       The unique identifer of the document in DocumentCloud's system. This is a number.
       ``83251``

   .. attribute:: json_text_url 

       A link to the static resource where the full text of the document, in a custom JSON format, indexed by page is available. 

   .. attribute:: language

      The three character code for the language this document is in.

   .. attribute:: large_image

       Returns the binary data for the "large" sized image of the document's first
       page. If you would like the data for some other page, pass the page number
       into ``get_large_image(page)``.

   .. attribute:: large_image_url

       Returns a URL containing the "large" sized image of the document's first
       page. If you would like the URL for some other page, pass the page number
       into ``get_large_image_url(page)``.

   .. attribute:: large_image_url_list

       Returns a list of URLs for the "large" sized image of every page in the document.

   .. attribute:: mentions

       When the document has been retrieved via a search, this returns a list of
       places the search keywords appear in the text. You must pass
       mentions = True into the search. The data is modeled by
       its own Python class, :class:`documentcloud.documents.Mention`.

           >>> obj_list = client.documents.search('Christopher Wallace', mentions=True)
           >>> obj = obj_list[0]
           >>> obj.mentions
           [<Mention: Page 2>, <Mention: Page 3> ....

   .. attribute:: noindex

       A boolean indicating whether the document is hidden from search engines and DocumentCloud search.
       A document may be public and embedded on a site, but still have noindex set to True so that the document isn't indexed on search engines. Private documents of course are not searchable on search engines regardless. 

   .. attribute:: normal_image

       Returns the binary data for the "normal" sized image of the document's
       first page. If you would like the data for some other page, pass the page
       number into ``get_normal_image(page)``.

   .. attribute:: normal_image_url

       Returns a URL containing the "normal" sized image of the document's first
       page. If you would like the URL for some other page, pass the page number
       into ``get_normal_image_url(page)``.

   .. attribute:: normal_image_url_list

       Returns a list of URLs for the "normal" sized image of every page in the document.

   .. attribute:: organization

      The :class:`documentcloud.organizations.Organization` which owns this
      document.  This will require an additional API call unless you specify
      `"organization"` in the `expand` parameter when fetching this document.

   .. attribute:: organization_id

      The ID for the organization which owns this document

   .. attribute:: original_extension

      The original file extension of the document before it was converted into a PDF during DocumentCloud processing. 

   .. attribute:: page_count

       Alias for :attr:`pages`.

   .. attribute:: page_spec

      The page spec is a compressed string that lists dimensions in pixels for every
      page in a document. Refer to ListCrunch_ for the compression format. For
      example, `612.0x792.0:0-447`

   .. attribute:: pages

       The number of pages in the document.

   .. attribute:: page_position_json

       The raw positions of text on the first page, in a custom JSON format. Consult the API documentation for more details. Each unit (word or letter) in the document will have coordinates. To get a different page use ``get_page_position_json(page)``. 

   .. attribute:: page_position_json_url

       A link to the static asset where the first page of page positions in custom JSON format is available. Each unit (word or letter) in the document will have coordinates. To get a link to a different page use 
       ``get_page_position_json_url(page)``. If the document is public, the URL will point to S3, otherwise it will point to an internal DocumentCloud URL to verify that the user has permissions to view the page.

   .. attribute:: page_text

       The document's first page in plaintext format. To get a different page use 
       ``get_page_text(page)``. 

   .. attribute:: page_text_url

       A link to the static asset where the document's first page in plaintext format is available. To get a different page use ``get_page_text_url(page)``. If the document is public, the URL will point to S3, otherwise it will point to an internal DocumentCloud URL to verify that the user has permissions to view the page.

   .. attribute:: pdf

       Returns the binary data for document's original PDF file.

   .. attribute:: pdf_url

       Returns a URL containing the binary data for document's original PDF file.

   .. attribute:: projects

      Returns a list of IDs for the projects this document is in.

   .. attribute:: publish_at

       A timestamp (Date Time) when to automatically make this document public in a scheduled manner.

   .. attribute:: published_url

       Returns an URL outside of documentcloud.org where this document has been published.

   .. attribute:: related_article

       Returns an URL for a news story related to this document.
   
   .. attribute:: revision_control

       A boolean indicating whether or not this document has revision control enabled. 
       Revision control is only available to DocumentCloud premium users. 

   .. attribute:: sections

      A client to access and update the sections on the document.  See
      :class:`documentcloud.sections.Section` for more information.

   .. attribute:: slug

      Returns the document's slug.  A slug is a URL friendly version of the title.

   .. attribute:: small_image

       Returns the binary data for the "small" sized image of the document's first
       page. If you would like the data for some other page, pass the page number
       into ``get_small_image(page)``.

   .. attribute:: small_image_url

       Returns a URL containing the "small" sized image of the document's first
       page. If you would like the URL for some other page, pass the page number
       into ``get_small_image_url(page)``.

   .. attribute:: small_image_url_list

       Returns a list of URLs for the "small" sized image of every page in the document.

   .. attribute:: source

       The original source of the document. Can be edited and saved with a put command.

   .. attribute:: status

      This is the status of the document.  Possible statuses include:

      * `success`: The document has been succesfully processed
      * `readable`: The document is currently processing, but is readable during the operation
      * `pending`: The document is processing and not currently readable
      * `error`: There was an [error](#errors) during processing
      * `nofile`: The document was created, but no file was uploaded yet

   .. attribute:: thumbnail_image

       Returns the binary data for the "thumbnail" sized image of the document's
       first page. If you would like the data for some other page, pass the page
       number into ``get_thumbnail_image(page)``.

   .. attribute:: thumbnail_image_url

       Returns a URL containing the "thumbnail" sized image of the document's
       first page. If you would like the URL for some other page, pass the page
       number into ``get_thumbnail_image_url(page)``.

   .. attribute:: thumbnail_image_url_list

       Returns a list of URLs for the "thumbnail" sized image of every page in the document.

   .. attribute:: title

       The name of the document. Can be edited and saved with a put command.

   .. attribute:: updated_at

       The date and time that the document was last updated, in Python's datetime format.

   .. attribute:: user

      The :class:`documentcloud.users.User` which owns this document.  This
      will require an additional API call unless you specify `"user"` in the
      `expand` parameter when fetching this document.

   .. attribute:: user_id

      The ID for the user which owns this document

   .. attribute:: writable_fields

      Useful quick reference list for which fields a user may modify. 
      Includes `access`, `data`, `description`, `language`, `publish_at`, `published_url`, `related_article`, `source`, and `title`. 

   .. attribute:: xlarge_image

       Returns the binary data for the "xlarge" sized image of the document's
       first page. If you would like the data for some other page, pass the page
       number into ``get_xlarge_image(page)``.

   .. attribute:: xlarge_image_url

       Returns a URL containing the "xlarge" sized image of the document's
       first page. If you would like the URL for some other page, pass the page
       number into ``get_xlarge_image_url(page)``.

   .. attribute:: xlarge_image_url_list

       Returns a list of URLs for the "xlarge" sized image of every page in the document.


Mentions
--------

.. class:: documentcloud.documents.Mention

   Mentions of a search keyword found in one of the documents.

   .. attribute:: page

       The page where the mention occurs.

   .. attribute:: text

       The text surrounding the mention of the keyword.
