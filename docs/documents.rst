Documents
=========

Methods for drawing down, editing and uploading data about documents.

Retrieval
---------

.. method:: client.documents.get(id_, expand=None)

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


.. method:: client.documents.search(query, **params)

    Return a list of documents that match the provided query. ::

            >>> from documentcloud import DocumentCloud
            >>> client = DocumentCloud()
            >>> obj_list = client.documents.search('Ruben Salazar')
            >>> obj_list[0]
            <Document: Final OIR Report>

   The params may be set to any parameters that the search end point takes.
   Please see the full `search documentation
   <https://beta.documentcloud.org/help/search/>`_ for query syntax and
   available parameters.


.. method:: client.documents.list(self, **params)

   Return a list of all documents, possibly filtered by the given parameters.
   Please see the full `API documentation <https://beta.documentcloud.org/help/API/>`_
   for available parameters.


.. method:: client.documents.all(self, **params)

    An alias for :meth:`list`.



Editing
-------

.. method:: document_obj.put()

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
        >>> print obj.title
        Draft OIR Report
        >>> # Change its title
        >>> obj.title = "Brand new title"
        >>> print obj.title
        Brand New Title
        >>> # Save those changes
        >>> obj.put()

.. method:: document_obj.save()

    An alias for :meth:`put` that saves changes back to DocumentCloud.

.. method:: document_obj.delete()

   Delete a document from DocumentCloud. You must be authorized to make these changes. ::

        >>> obj = client.documents.get('71072-oir-final-report')
        >>> obj.delete()


Uploading
---------

.. method:: client.documents.upload(pdf, **kwargs)

   Upload a PDF to DocumentCloud. You must be authorized to do this. Returns
   the object representing the new record you've created. You can submit either
   a file path or a file object.

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> new_id = client.documents.upload("/home/ben/test.pdf", "Test PDF")
        >>> # Now fetch it
        >>> client.documents.get(new_id)
        <Document: Test PDF>

    You can also use URLs which link to PDFs, if that's the kind of thing you
    want to do.

        >>> client.documents.upload("http://ord.legistar.com/Chicago/attachments/e3a0cbcb-044d-4ec3-9848-23c5692b1943.pdf")

    You may set the ``kwargs`` to any of the writable attributes as described
    in :meth:`put`.  Additionally, you may set ``force_ocr`` in order to force
    OCR to take place even if the document has embedded text, as well as either
    ``project`` to the ID of a project to upload the document into, or
    ``projects``, a list of project IDs to upload the document into.

.. method:: client.documents.upload_directory(pdf, **kwargs)

   Searches through the provided path and attempts to upload all the PDFs it
   can find. Metadata, which accepts the same keywords as :meth:`upload`,
   provided to the other keyword arguments will be recorded for all uploads
   (except for title which will be set based on the filename). Returns a list
   of document objects that are created. Be warned, this will upload any
   documents in directories inside the path you specify.

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)
        >>> obj_list = client.documents.upload_directory('/home/ben/pdfs/groucho_marx/')

Metadata
--------

.. attribute:: document_obj.access

    The privacy level of the resource within the DocumentCloud system. It will
    be either ``public``, ``private`` or ``organization``, the last of which
    means the is only visible to members of the contributors organization. Can
    be edited and saved with a put command.

.. XXX document the annotations and sections child client functionality

.. attribute:: document_obj.annotations
    
    A list of the annotations users have left on the document. The data are
    modeled by their own Python class, defined in the :ref:`annotations`
    section.

        >>> obj = client.documents.get('83251-fbi-file-on-christopher-biggie-smalls-wallace')
        >>> obj.annotations
        [<Annotation>, <Annotation>, <Annotation>, <Annotation>, <Annotation>]

.. attribute:: document_obj.asset_url

.. attribute:: document_obj.canonical_url

    The URL where the document is hosted at documentcloud.org.

.. attribute:: document_obj.contributor

    The user who originally uploaded the document.

.. attribute:: document_obj.contributor_organization

    The organizational affiliation of the user who originally uploaded the document.

.. attribute:: document_obj.created_at

    The date and time that the document was created, in Python's datetime format.

.. attribute:: document_obj.data

    A dictionary containing supplementary data linked to the document. This can
    be any old thing. It's useful if you'd like to store additional metadata.
    Can be edited and saved with a put command.

        >>> obj = client.documents.get('83251-fbi-file-on-christopher-biggie-smalls-wallace')
        >>> obj.data
        {'category': 'hip-hop', 'byline': 'Ben Welsh', 'pub_date': datetime.date(2011, 3, 1)}

    Keys must be strings and only contain alphanumeric characters.


.. attribute:: document_obj.description

    A summary of the document. Can be edited and saved with a put command.

.. attribute:: document_obj.edit_access

.. attribute:: document_obj.file_hash

    A hash representation of the raw PDF data as a hexadecimal string.

        >>> obj = client.documents.get('1021571-lafd-2013-hiring-statistics')
        >>> obj.file_hash
        '872b9b858f5f3e6bb6086fec7f05dd464b60eb26'

    You could recreate this hexadecimal hash yourself using the `SHA-1
    algorithm <https://en.wikipedia.org/wiki/SHA-1>`_.

        >>> import hashlib
        >>> hashlib.sha1(obj.pdf).hexdigest()
        '872b9b858f5f3e6bb6086fec7f05dd464b60eb26'

.. attribute:: document_obj.full_text

    Returns the full text of the document, as extracted from the original PDF by DocumentCloud. Results may vary, but this will give you what they got. Currently, DocumentCloud only makes this available for public documents.

        >>> obj = client.documents.get('71072-oir-final-report')
        >>> obj.full_text
        "Review of the Los Angeles County Sheriff's\nDepartment's Investigation
        into the\nHomicide of Ruben Salazar\nA Special Report by the\nLos
        Angeles County Office of Independent Review\n ...

.. attribute:: document_obj.full_text_url

    Returns the URL that contains the full text of the document, as extracted
    from the original PDF by DocumentCloud.

.. method:: document_obj.get_page_text(page)

    Submit a page number and receive the raw text extracted from it by DocumentCloud.

    >>> obj = client.documents.get('1088501-adventuretime-alta')
    >>> txt = obj.get_page_text(1)
    # Let's print just the first line
    >>> print txt.decode().split("\n")[0]
    STATE OF CALIFORNIA- HEALTH AND HUMAN SERVICES AGENCY

.. attribute:: document_obj.id

    The unique identifer of the document in DocumentCloud's system. This is a number.
    ``83251``

.. attribute:: document_obj.language

.. attribute:: document_obj.large_image

    Returns the binary data for the "large" sized image of the document's first
    page. If you would like the data for some other page, pass the page number
    into ``document_obj.get_large_image(page)``. Currently, DocumentCloud only
    makes this available for public documents.

.. attribute:: document_obj.large_image_url

    Returns a URL containing the "large" sized image of the document's first
    page. If you would like the URL for some other page, pass the page number
    into ``document_obj.get_large_image_url(page)``.

.. attribute:: document_obj.large_image_url_list

    Returns a list of URLs for the "large" sized image of every page in the document.

.. attribute:: document_obj.mentions

    When the document has been retrieved via a search, this returns a list of
    places the search keywords appear in the text. The data are modeled by
    their own Python class, defined in the :ref:`mentions` section.

        >>> obj_list = client.documents.search('Christopher Wallace')
        >>> obj = obj_list[0]
        >>> obj.mentions
        [<Mention: Page 2>, <Mention: Page 3> ....

.. attribute:: document_obj.normal_image

    Returns the binary data for the "normal" sized image of the document's
    first page. If you would like the data for some other page, pass the page
    number into ``document_obj.get_normal_image(page)``. Currently,
    DocumentCloud only makes this available for public documents.

.. attribute:: document_obj.normal_image_url

    Returns a URL containing the "normal" sized image of the document's first
    page. If you would like the URL for some other page, pass the page number
    into ``document_obj.get_normal_image_url(page)``.

.. attribute:: document_obj.normal_image_url_list

    Returns a list of URLs for the "normal" sized image of every page in the document.

.. XXX organization, expand, cache, ref organization object

.. attribute:: document_obj.organization

.. attribute:: document_obj.page_count

    Alias for :attr:`pages`.

.. attribute:: document_obj.page_spec

.. attribute:: document_obj.pages

    The number of pages in the document.

.. attribute:: document_obj.pdf

    Returns the binary data for document's original PDF file. Currently,
    DocumentCloud only makes this available for public documents.

.. attribute:: document_obj.pdf_url

    Returns a URL containing the binary data for document's original PDF file.

.. attribute:: document_obj.projects

.. attribute:: document_obj.published_url

    Returns an URL outside of documentcloud.org where this document has been published.

.. attribute:: document_obj.related_article

    Returns an URL for a news story related to this document.

.. XXX
.. attribute:: document_obj.sections

    A list of the sections earmarked in the text by a user. The data are
    modeled by their own Python class, defined in the :ref:`sections` section.

        >>> obj = client.documents.get('74103-report-of-the-calpers-special-review')
        >>> obj.sections
        [<Section: Letter to Avraham Shemesh and Richard Resller of SIM Group>, <Section: Letter to Ralph Whitworth, founder of Relational Investors>, ...

.. attribute:: document_obj.slug

.. attribute:: document_obj.small_image

    Returns the binary data for the "small" sized image of the document's first
    page. If you would like the data for some other page, pass the page number
    into ``document_obj.get_small_image(page)``. Currently, DocumentCloud only
    makes this available for public documents.

.. attribute:: document_obj.small_image_url

    Returns a URL containing the "small" sized image of the document's first
    page. If you would like the URL for some other page, pass the page number
    into ``document_obj.get_small_image_url(page)``.

.. attribute:: document_obj.small_image_url_list

    Returns a list of URLs for the "small" sized image of every page in the document.

.. attribute:: document_obj.source

    The original source of the document. Can be edited and saved with a put command.

.. attribute:: document_obj.status

.. attribute:: document_obj.thumbnail_image

    Returns the binary data for the "thumbnail" sized image of the document's
    first page. If you would like the data for some other page, pass the page
    number into ``document_obj.get_thumbnail_image(page)``. Currently,
    DocumentCloud only makes this available for public documents.

.. attribute:: document_obj.thumbnail_image_url

    Returns a URL containing the "thumbnail" sized image of the document's
    first page. If you would like the URL for some other page, pass the page
    number into ``document_obj.get_small_thumbnail_url(page)``.

.. attribute:: document_obj.thumbnail_image_url_list

    Returns a list of URLs for the "small" sized image of every page in the document.

.. attribute:: document_obj.title

    The name of the document. Can be edited and saved with a put command.

.. attribute:: document_obj.updated_at

    The date and time that the document was last updated, in Python's datetime format.

.. attribute:: document_obj.user
