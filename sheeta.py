import os
from gdata.docs.service import DocsService, DocumentQuery
from gdata.spreadsheet.service import SpreadsheetsService


class Connection(object):
    """ The connection controls user credentials and the connections
    to various google services. """

    def __init__(self, google_user=None, google_password=None):
        self._google_user = google_user
        self._google_password = google_password

    @property
    def google_user(self):
        return self._google_user or os.environ.get('GOOGLE_USER')

    @property
    def google_password(self):
        return self._google_password or os.environ.get('GOOGLE_PASSWORD')

    @property
    def docs_client(self):
        if not hasattr(self, '_docs_client'):
            client = DocsService()
            client.ClientLogin(self.google_user, self.google_password)
            self._docs_client = client
        return self._docs_client

    @property
    def sheets_client(self):
        if not hasattr(self, '_sheets_client'):
            client = SpreadsheetsService()
            client.email = self.google_user
            client.password = self.google_password
            client.source = 'Sheeta'
            client.ProgrammaticLogin()
            self._sheets_client = client
        return self._sheets_client

    @classmethod
    def connect(cls, conn=None, google_user=None,
                google_password=None):
        if conn is None:
            conn = cls(google_user=google_user,
                       google_password=google_password)
        return conn


class Spreadsheet(object):
    """ A simple wrapper for google docs spreadsheets. """

    def __init__(self, id, conn):
        self.id = id
        self.conn = conn

    @property
    def client(self):
        return self.conn.sheets_client

    @property
    def meta(self):
        if not hasattr(self, '_wsf') or self._wsf is None:
            self._wsf = self.client.GetWorksheetsFeed(self.id)
        return self._wsf

    @property
    def title(self):
        return self.meta.title.text

    def __repr__(self):
        return '<Spreadsheet(%r, %r)>' % (self.id, self.title)

    def __unicode__(self):
        return self.id

    @classmethod
    def by_id(cls, id, conn=None, google_user=None,
              google_password=None):
        conn = Connection.connect(conn=conn, google_user=google_user,
                                  google_password=google_password)
        return cls(id=id, conn=conn)

    @classmethod
    def by_title(cls, title, conn=None, google_user=None,
                 google_password=None):
        conn = Connection.connect(conn=conn, google_user=google_user,
                                  google_password=google_password)
        q = DocumentQuery(categories=['spreadsheet'],
                          text_query=title)
        feed = conn.docs_client.Query(q.ToUri())
        for entry in feed.entry:
            if title == entry.title.text:
                id = entry.feedLink.href.rsplit('%3A', 1)[-1]
                return cls.by_id(id, conn=conn)
