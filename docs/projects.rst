Projects
========

Methods for drawing down, editing and uploading data about DocumentCloud
projects. A project is a group of documents.

ProjectClient
-------------

.. class:: documentcloud.projects.ProjectClient

   The project client gives access to retrieval and creation of projects.
   It is generally accessed as ``client.projects``.

   .. method:: all(**params)

      Return all projects for the authorized DocumentCloud account.
      Please see the full `API documentation`_ for available parameters. ::

           >>> from documentcloud import DocumentCloud
           >>> client = DocumentCloud(USERNAME, PASSWORD)
           >>> obj_list = client.projects.all()
           >>> obj_list[0]
           <Project: Ruben Salazar>

   .. method:: create(title, description="", private=True, document_ids=None)

      Create a new project on DocumentCloud. You must be authorized to do this.
      Returns the object representing the new record you've created.

           >>> from documentcloud import DocumentCloud
           >>> client = DocumentCloud(USERNAME, PASSWORD)
           >>> obj = client.projects.create("New project")
           >>> obj
           <Project: New project>

   .. method:: get(id=None, title=None)

      Return the project with the provided DocumentCloud identifer. You can
      retrieve projects using either the `id` or `title`. ::

           >>> from documentcloud import DocumentCloud
           >>> client = DocumentCloud(USERNAME, PASSWORD)
           >>> # Fetch using the id
           >>> obj = client.projects.get(id='816')
           >>> obj
           <Project: The Ruben Salazar Files>
           >>> # Fetch using the title
           >>> obj = client.projects.get(title='The Ruben Salazar Files')
           >>> obj
           <Project: The Ruben Salazar Files>

   .. method:: get_or_create_by_title(title)

      Fetch the project with provided name, or create it if it does not exist. You
      must be authorized to do this. Returns a tuple. An object representing the
      record comes first. A boolean that reports whether or not the objects was
      created fresh comes second. It is true when the record was created, false
      when it was found on the site already.

           >>> from documentcloud import DocumentCloud
           >>> client = DocumentCloud(USERNAME, PASSWORD)
           >>> # The first time it will be created and added to documentcloud.org
           >>> obj, created = client.projects.get_or_create_by_title("New project")
           >>> obj, created
           <Project: New project>, True
           >>> # The second time it will be fetched from documentcloud.org
           >>> obj, created = client.projects.get_or_create_by_title("New project")
           >>> obj, created
           <Project: New project>, False

   .. method:: get_by_id(id)

      Return the project with the provided id. Operates the same as
      `client.projects.get`.

   .. method:: get_by_title(title)

      Return the project with the provided title. Operates the same as
      `client.projects.get`.

   .. method:: list(**params)

      List all projects.
      Please see the full `API documentation`_ for available parameters.

Project
-------

.. class:: documentcloud.projects.Project

   An individual project, as obtained by the :class:`documentcloud.projects.ProjectClient`.

   .. method:: put()

      Save changes to a project back to DocumentCloud. You must be authorized to
      make these changes. Only the
      :attr:`description`,
      :attr:`document_list`,
      :attr:`private`,
      and :attr:`title`,
      attributes may be edited. ::

           >>> obj = client.projects.get('816')
           >>> obj.title = "Brand new title"
           >>> obj.put()

   .. method:: save()

       An alias for :meth:`put` that saves changes back to DocumentCloud.

   .. method:: delete()

      Delete a project from DocumentCloud. You must be authorized to make these
      changes. ::

           >>> obj = client.projects.get('816')
           >>> obj.delete()
   
   .. method:: clear_documents()

      Removes all documents from a project. 

         >>> obj = client.projects.get('816')
         >>> obj.clear_documents()
   
   .. method:: add_documents()

      Efficiently adds a lot of documents to a project. 
      Adds the documents 25 at a time using bulk API calls. 

         >>> documents_to_add = [client.documents.get('23745990'), client.documents.get('23745988')]
         >>> obj = client.projects.get('816')
         >>> obj.add_documents(documents_to_add)
         >>> obj.put()

   .. attribute:: created_at

      The date and time when this project was created

   .. attribute:: description

       A summary of the project. Can be edited and saved with a put command.

   .. attribute:: document_ids

       A list that contains the unique identifier of the documents assigned to
       this project. Cannot be edited. Edit the document_list instead.

           >>> obj = client.projects.get('816')
           >>> obj.document_ids
           [19419, 19420, 19280, 19281, ...

   .. attribute:: document_list

       A list that documents assigned to this project. Can be expanded by
       appending new documents to the list or cleared by reassigning it as an
       empty list and then issuing the put command.

           >>> obj = client.projects.get('816')
           >>> obj.document_list
           [<Document: Times Columnist Ruben Salazar Slain by Tear-gas Missile>, <Document: Salazar's Legacy Lives On>, <Document: Cub Reporter Catches Attention of El Paso FBI>, ...

   .. attribute:: documents

       Alias for :attr:`document_list`.

   .. attribute:: edit_access

      A boolean indicating whether or not you have the ability to save this project.

   .. method:: get_document(id)

           Retrieves a particular document from the project using the provided
           DocumentCloud identifer.

   .. attribute:: id

       The unique identifer of the project in DocumentCloud's system. Typically
       this is a number.

   .. attribute:: private

      Whether or not this project is private.  Private documents in public
      projects will not be viewable, but setting a project to private will protect
      its existence from being publically viewable.

   .. attribute:: slug

      The slug for the project.  A slug is a URL friendly version of the title.

   .. attribute:: title

       The name of the project. Can be edited and saved with a put command.

   .. attribute:: updated_at

      The date and time of the last time this project was updated.

   .. attribute:: user

      The ID of the :class:`documentcloud.users.User` who created this project.
