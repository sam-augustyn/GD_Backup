#!/usr/bin/env python
import os
import datetime

directory = ""
save = ""

now = datetime.datetime.now()
date = str(now.month)+str(now.day)+str(now.year-2000)
os.system("zip -r %s/project%s.zip %s" % (save, date, directory))

'''file_metadata = {'name': 'project%s.zip' % (date)}
media = MediaFileUpload('%s/project%s' % (save, date),mimetype='application/zip')
file = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
print 'File ID: %s' % file.get('id')'''
