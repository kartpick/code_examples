from class_db import Database
import json, uuid
from storage import storage
from ..config import CONFIG
from localization import get_encoding
from datetime import datetime
from ..lib.xappy_fulltextsearch import fulltextsearch
from ..lib.xappy_indexconnector import indexconnector
from class_user import User
from flask import request


class Link():
    def __init__(self, row=None):

        if row:
            self.guid           = row[1]
            self.documents      = json.loads(row[2])
            self.del_date       = datetime.strptime(row[3], self.date_format)
            self.folder_guid    = row[4]
            self.type           = row[5]
        else:
            self.guid           = ""
            self.documents      = []
            self.del_date       = ""
            self.folder_guid    = ""
            self.type           = ""


    def save(self):
        if not self.guid:
            self.guid = str(uuid.uuid4())

        json_data = json.dumps(self.documents)
        query = """ mysql query """
        Database.maindb().commit(query, (
            self.guid,
            json_data,
            self.del_date.strftime(self.date_format),
            self.dshare_guid,
            self.type))

        return self.guid


    @classmethod
    def get_all(cls):
        query = """ mysql query """
        rows = Database.maindb().fetch_all(query)

        return [Sharing(row) for row in rows]


    @classmethod
    def delete(cls, guid):
        query = """ mysql query """
        Database.maindb().commit(query, (str(guid),))


    @classmethod
    def delete_outdated(cls):
        for link in cls.get_all():
            if link.del_date <= datetime.now():
                cls.delete(link.guid)


    @classmethod
    def get_by_guid(cls, guid):
        query = """ mysql query """
        row = Database.maindb().fetch_one(query, (str(guid),))

        if row:
            return Sharing(row)
        return None


    def send_share_by_email(self, email, theme, ):
        from class_mail import Mailer

        domain = request.environ["HTTP_HOST"].split(':')[0].encode("utf-8")
        mail_theme = theme
        mail_text = """ link template """ % { """link_data""" }
        attachment = []
        sender = u"notifications@%(domain)s" % { "domain": domain}

        sent = Mailer.send(sender, email, mail_theme, mail_text, attachment)
        result = "mail_fsend_err" if not sent else "mail_fsend_ok"

        return result

    def zip_documents_to_file(self):
        """
            zip_documents_to_file: zips documents into file and returns filename"""
        import os
        import zipfile
        from document_class import Document

        zipfilename = os.path.join(os.getcwd(),
            CONFIG['TEMP-DIRECTORY'],
            "%s.zip" % self.guid.encode("utf8"))

        zf = zipfile.ZipFile(zipfilename, mode='w')
        files = []

        docs_folder = Document.get_by_folder_guid(self.folder_guid)
        
        xconn = indexconnector()
        xsearch = fulltextsearch()

        docs_folder.set_connector(xconn)
        docs_folder.set_search(xsearch)

        real_path = docs_folder.complete_path()


        # For all package files
        for doc_guid in self.documents:

            doc = docs_folder.get_doc_by_db_id(doc_guid)

            # if suddenly file is not exists -> ignore doc
            if not storage.exists(real_path) or not doc:
                continue

            doc_name = doc.filename(True)

            i = 0
            while doc_name in files:  # check for same-named files
                i += 1
                f_name, f_ext = os.path.splitext(docs_folder.get_doc_name(doc_guid))
                doc_name = "%s_%s" % (f_name, str(i) + f_ext)

            doc_name = doc_name.encode(get_encoding(), "ignore")

            files.append(doc_name)
            zf.write(storage.abs_path("/".join((real_path, doc_guid))), doc_name)
        zf.close()
        
        return zipfilename