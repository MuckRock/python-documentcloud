"""
Python library for interacting with the DocumentCloud API.

DocumentCloud's API can search, upload, edit and organize documents hosted
in its system. Public documents are available without an API key, but 
authorization is required to interact with private documents.

Further documentation:

    https://www.documentcloud.org/help/api

"""
import base64
import urllib, urllib2
from datetime import datetime
from dateutil.parser import parse as dateparser
try:
    import json
except ImportError:
    import simplejson as json

#
# API objects
#

class BaseAPIObject(object):
    """
    An abstract version of the objects returned by the API.
    """
    def __init__(self, d):
        self.__dict__ = d
    
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.__str__())
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")
    
    def __unicode__(self):
        return unicode(self.title)


class Document(BaseAPIObject):
    """
    A document returned by the API.
    """
    def __init__(self, d):
        self.__dict__ = d
        self.resources = Resource(d.get("resources"))
        self.created_at = dateparser(d.get("created_at"))
        self.updated_at = dateparser(d.get("updated_at"))
    
    #
    # Updates
    #
    
    def put(self):
        """
        Save changes made to the object to DocumentCloud.
        
        According to DocumentCloud's docs, edits are allowed for the following
        fields:
        
            * title
            * source
            * description
            * related_article
            * access
            * published_url
            #
    # Updates
    #
    
    def put(self):
        """
        Save changes made to the object to DocumentCloud.
        
        According to DocumentCloud's docs, edits are allowed for the following
        fields:
        
            * title
            * source
            * description
            * related_article
            * access
            * published_url
        
        Returns nothing.
        """
        params = dict(
            title=self.title,
            source=self.source,
            description=self.description,
            related_article=self.resources.related_article,
            published_url=self.resources.published_url,
            access=self.access,
        )
        self._connection.put('documents/%s.json' % self.id, params)
        Returns nothing.
        """
        params = dict(
            title=self.title,
            source=self.source,
            description=self.description,
            related_article=self.resources.related_article,
            published_url=self.resources.published_url,
            access=self.access,
        )
        self._connection.put('documents/%s.json' % self.id, params)
    
    #
    # Lazy loaded attributes
    #
    
    def get_contributor(self):
        """
        Fetch the contributor field if it does not exist.
        """
        try:
            return self.__dict__[u'contributor']
        except KeyError:
            obj = self._connection.documents.get(id=self.id)
            self.__dict__[u'contributor'] = obj.contributor
            return obj.contributor
    contributor = property(get_contributor)
    
    def get_contributor_organization(self):
        """
        Fetch the contributor_organization field if it does not exist.
        """
        try:
            return self.__dict__[u'contributor_organization']
        except KeyError:
            obj = self._connection.documents.get(id=self.id)
            self.__dict__[u'contributor_organization'] = obj.contributor_organization
            return obj.contributor_organization
    contributor_organization = property(get_contributor_organization)
    
    def get_annotations(self):
        """
        Fetch the annotations field if it does not exist.
        """
        try:
            obj_list = self.__dict__[u'annotations']
            return [Annotation(i) for i in obj_list]
        except KeyError:
            obj = self._connection.documents.get(id=self.id)
            obj_list = [Annotation(i) for i in obj.__dict__['annotations']]
            self.__dict__[u'annotations'] =obj.__dict__['annotations']
            return obj_list
    annotations = property(get_annotations)
    
    def get_sections(self):
        """
        Fetch the sections field if it does not exist.
        """
        try:
            obj_list = self.__dict__[u'sections']
            return [Section(i) for i in obj_list]
        except KeyError:
            obj = self._connection.documents.get(id=self.id)
            obj_list = [Section(i) for i in obj.__dict__['sections']]
            self.__dict__[u'sections'] = obj.__dict__['sections']
            return obj_list
    sections = property(get_sections)
    
    def get_entities(self):
        """
        Fetch the entities extracted from this document by OpenCalais.
        """
        try:
            return self.__dict__[u'entities']
        except KeyError:
            data = self._connection.fetch("documents/%s/entities.json" % self.id).get("entities")
            obj_list = []
            for type, entity_list in data.items():
                for entity in entity_list:
                    entity['type'] = entity
                    obj = Entity(entity)
                    obj_list.append(obj)
            self.__dict__[u'entities'] = obj_list
            return obj_list
    entities = property(get_entities)
    
    #
    # Text
    #
    
    def get_full_text_url(self):
        """
        Returns the URL that contains the full text of the document.
        """
        return self.resources.text
    full_text_url = property(get_full_text_url)
    
    def get_full_text(self):
        """
        Downloads and returns the full text of the document.
        """
        req = urllib2.Request(self.full_text_url)
        response = urllib2.urlopen(req)
        return response.read()
    full_text = property(get_full_text)
    
    def get_page_text_url(self, page):
        """
        Returns the URL for the full text of a particular page in the document.
        """
        template = self.resources.page.get('text')
        url = template.replace("{page}", str(page))
        return url
    
    def get_page_text(self, page):
        """
        Downloads and returns the full text of a particular page in the document.
        """
        url = self.get_page_text_url(page)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()
    
    #
    # Images
    #
    
    def get_pdf_url(self):
        """
        Returns the URL that contains the full PDF of the document.
        """
        return self.resources.pdf
    pdf_url = property(get_pdf_url)
    
    def get_pdf(self):
        """
        Downloads and returns the full PDF of the document.
        """
        req = urllib2.Request(self.pdf_url)
        response = urllib2.urlopen(req)
        return response.read()
    pdf = property(get_pdf)
    
    def get_small_image_url(self, page=1):
        """
        Returns the URL for the small sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        url = template.replace("{page}", str(page)).replace("{size}", "small")
        return url
    small_image_url = property(get_small_image_url)
    
    def get_thumbnail_image_url(self, page=1):
        """
        Returns the URL for the thumbnail sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        url = template.replace("{page}", str(page)).replace("{size}", "thumbnail")
        return url
    thumbnail_image_url = property(get_thumbnail_image_url)
    
    def get_large_image_url(self, page=1):
        """
        Returns the URL for the large sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        url = template.replace("{page}", str(page)).replace("{size}", "large")
        return url
    large_image_url = property(get_large_image_url)
    
    def get_small_image_url_list(self):
        """
        Returns a list of the URLs for the small sized image of every page.
        """
        return [self.get_small_image_url(i) for i in range(1, self.pages +1)]
    small_image_url_list = property(get_small_image_url_list)
    
    def get_thumbnail_image_url_list(self):
        """
        Returns a list of the URLs for the thumbnail sized image of every page.
        """
        return [self.get_thumbnail_image_url(i) for i in range(1, self.pages +1)]
    thumbnail_image_url_list = property(get_thumbnail_image_url_list)
    
    def get_large_image_url_list(self):
        """
        Returns a list of the URLs for the large sized image of every page.
        """
        return [self.get_large_image_url(i) for i in range(1, self.pages +1)]
    large_image_url_list = property(get_large_image_url_list)
    
    def get_small_image(self, page=1):
        """
        Downloads and returns the small sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        url = self.get_small_image_url(page=page)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()
    small_image = property(get_small_image)
    
    def get_thumbnail_image(self, page=1):
        """
        Downloads and returns the thumbnail sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        url = self.get_thumbnail_image_url(page=page)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()
    thumbnail_image = property(get_thumbnail_image)
    
    def get_large_image(self, page=1):
        """
        Downloads and returns the large sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        url = self.get_large_image_url(page=page)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()
    large_image = property(get_large_image)


class Project(BaseAPIObject):
    """
    A project returned by the API.
    """
    #
    # Updates
    #
    
    def put(self):
        """
        Save changes made to the object to DocumentCloud.
        
        According to DocumentCloud's docs, edits are allowed for the following
        fields:
        
            * title
            * description
            * document_ids
        
        Returns nothing.
        """
        params = dict(
            title=self.title,
            description=self.description,
            document_ids=[str(i.id) for i in self.document_list]
        )
        self._connection.put('projects/%s.json' % self.id, params)
    
    #
    # Documents
    #
    
    def get_document_list(self):
        """
        Retrieves all documents included in this project.
        """
        try:
            return self.__dict__[u'document_list']
        except KeyError:
            obj_list = [self._connection.documents.get(i) for i in self.document_ids]
            self.__dict__[u'document_list'] = obj_list
            return obj_list
    document_list = property(get_document_list)
    
    def get_document(self, id):
        """
        Retrieves a particular document from this project.
        """
        obj_list = self.document_list
        matches = [i for i in obj_list if str(i.id) == str(id)]
        if not matches:
            raise DoesNotExistError("The resource you've requested does not exist or is unavailable without the proper credentials.")
        return matches[0]


class Section(BaseAPIObject):
    """
    A section earmarked inside of a Document
    """
    pass


class Entity(BaseAPIObject):
    """
    Keywords and such extracted from the document by OpenCalais.
    """
    def __unicode__(self):
        return unicode(self.value)


class Annotation(BaseAPIObject):
    """
    An annotation earmarked inside of a Document.
    """
    def __init__(self, d):
        self.__dict__ = d
    
    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")
    
    def __unicode__(self):
        return u''
    
    def get_location(self):
        """
        Return the location as a good
        """
        image_string =  self.__dict__['location']['image']
        image_ints = map(int, image_string.split(","))
        return Location(*image_ints)
    location = property(get_location)


class Location(object):
    """
    The location of a 
    """
    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")
    
    def __unicode__(self):
        return u''
    
    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left


class Resource(BaseAPIObject):
    """
    The resources associated with a Document. Hyperlinks and such.
    """
    def __repr__(self):
        return '<%ss>' % self.__class__.__name__
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")
    
    def __unicode__(self):
        return u''
    
    def __getattr__(self, name):
        # When these attrs don't exist in the DocumentCloud db,
        # they aren't included in the JSON. But we need to them
        # to come out as empty strings if someone tries to call
        # them here in Python.
        if name in ['related_article', 'published_url']:
            return ''
        else:
            raise AttributeError

#
# Exceptions
#

class CredentialsMissingError(Exception):
    """
    Raised if an API call is attempted without the required login credentials
    """
    pass


class CredentialsFailedError(Exception):
    """
    Raised if an API call fails because the login credentials are no good.
    """
    pass


class DoesNotExistError(Exception):
    """
    Raised when the user asks the API for something it cannot find.
    """
    pass

#
# API connection clients
#

class BaseDocumentCloudClient(object):
    """
    Patterns common to all of the different API methods.
    """
    BASE_URI = u'https://www.documentcloud.org/api/'
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def put(self, method, params):
        """
        Post changes back to DocumentCloud
        """
        if not self.username and not self.password:
            raise CredentialsMissingError("This is a private method. You must provide a username and password when you initialize the DocumentCloud client to attempt this type of request.")
        # Assemble the URL
        url = self.BASE_URI + method
        # Prepare the params
        params['_method'] = 'put'
        params = urllib.urlencode(params)
        # Create the request object
        request = urllib2.Request(url, params)
        credentials = '%s:%s' % (self.username, self.password)
        encoded_credentials = base64.encodestring(credentials).replace("\n", "")
        header = 'Basic %s' % encoded_credentials
        request.add_header('Authorization', header)
        # Make the request
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            if e.code == 404:
                raise DoesNotExistError("The resource you've requested does not exist or is unavailable without the proper credentials.")
            elif e.code == 401:
                raise CredentialsFailedError("The resource you've requested requires proper credentials.")
            else:
                raise e
    
    def fetch(self, method, params=None):
        """
        Fetch an url.
        """
        # Assemble the URL
        url = self.BASE_URI + method
        # Prepare any query string parameters
        if params:
            params = urllib.urlencode(params)
        # Create the request object
        args = [i for i in [url, params] if i]
        request = urllib2.Request(*args)
        # If the client has credentials, include them as a header
        if self.username and self.password:
            credentials = '%s:%s' % (self.username, self.password)
            encoded_credentials = base64.encodestring(credentials).replace("\n", "")
            header = 'Basic %s' % encoded_credentials
            request.add_header('Authorization', header)
        # Make the request
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            if e.code == 404:
                raise DoesNotExistError("The resource you've requested does not exist or is unavailable without the proper credentials.")
            elif e.code == 401:
                raise CredentialsFailedError("The resource you've requested requires proper credentials.")
            else:
                raise e
        # Read the response
        data = response.read()
        # Convert its JSON to a Python dictionary and return
        return json.loads(data)


class DocumentClient(BaseDocumentCloudClient):
    """
    Methods for collecting documents
    """
    def __init__(self, username, password, connection):
        self.username = username
        self.password = password
        # We want to have the connection around on all Document objects
        # this client creates in case the instance needs to hit the API
        # later. Storing it will preserve the credentials.
        self._connection = connection
    
    def _get_search_page(self, query, page, per_page):
        """
        Retrieve one page of search results from the DocumentCloud API.
        """
        params = {
            'q': query,
            'page': page,
            'per_page': per_page,
        }
        data = self.fetch(u'search.json', params)
        return data.get("documents")
    
    def search(self, query):
        """
        Retrieve all objects that make a search query.
        
        Example usage:
        
            >> documentcloud.documents.search('salazar')
        
        """
        page = 1
        document_list = []
        # Loop through all the search pages and fetch everything
        while True:
            results = self._get_search_page(query, page=page, per_page=1000)
            if results:
                document_list += results
                page += 1
            else:
                break
        obj_list = []
        for doc in document_list:
            doc['_connection'] = self._connection
            obj = Document(doc)
            obj_list.append(obj)
        return obj_list
    
    def get(self, id):
        """
        Retrieve a particular document using it's unique identifier.
        
        Example usage:
        
            >> documentcloud.documents.get(u'71072-oir-final-report')
        
        """
        data = self.fetch('documents/%s.json' % id).get("document")
        data['_connection'] = self._connection
        return Document(data)


class ProjectClient(BaseDocumentCloudClient):
    """
    Methods for collecting projects
    """
    def __init__(self, username, password, connection):
        self.username = username
        self.password = password
        # We want to have the connection around on all Document objects
        # this client creates in case the instance needs to hit the API
        # later. Storing it will preserve the credentials.
        self._connection = connection
    
    def all(self):
        """
        Retrieve all your projects. Requires authentication.
        
        Example usage:
        
            >> documentcloud.projects.all()
        
        """
        if not self.username and not self.password:
            raise CredentialsMissingError("This is a private method. You must provide a username and password when you initialize the DocumentCloud client to attempt this type of request.")
        project_list = self.fetch('projects.json').get("projects")
        obj_list = []
        for proj in project_list:
            proj['_connection'] = self._connection
            proj = Project(proj)
            obj_list.append(proj)
        return obj_list
    
    def get(self, id):
        """
        Retrieve a particular project using its unique identifier.
        
        Example usage:
        
            >> documentcloud.projects.get(u'arizona-shootings')
        
        """
        try:
            return [i for i in self.all() if str(i.id) == str(id)][0]
        except IndexError:
            raise DoesNotExistError("The resource you've requested does not exist or is unavailable without the proper credentials.")


class DocumentCloud(BaseDocumentCloudClient):
    """
    The public interface for the DocumentCloud API
    """
    
    def __init__(self, username=None, password=None):
        super(DocumentCloud, self).__init__(username, password)
        self.documents = DocumentClient(self.username, self.password, self)
        self.projects = ProjectClient(self.username, self.password, self)


if __name__ == '__main__':
    """
    Ignore all this. Ad hoc testing ground as I build the API piece by piece.
    """
    from pprint import pprint
    from private_settings import *
    public = DocumentCloud()
    private = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)
    bad = DocumentCloud("Bad", "Login")
    obj = private.documents.get(u'15144-mitchrpt')
    print obj.resources.related_article
    #print obj.title
    #obj.title = 'The Mitchell Report (w00t!)'
    #print obj.title
    #obj.put()




