#!/usr/bin/env python

import ftplib
import traceback
from datetime import datetime, timedelta
import os

class BackupScript():
    
    def __init__(self):
        self.server = 'u149656.your-backup.de'
        self.user_name = 'u149656'
        self.password = 'xbDnCbtJV7VcP8Wj'
        self.backup_path = 'backup_nextpulse'
    """
    def login_to_ftp_server(self, server, u_name, password):
        try:
            ftp = ftplib.FTP(server)    # Connect to the host with default port
            ftp.login(u_name, password)   # UserName, Password
        except Exception as e:
            print traceback.print_exc()

        return ftp

    def remove_old_files(self, ftp):
        old_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')

        try:
            files_list = [ftp.delete(f_name) for f_name in ftp.nlst() if old_date in f_name]
        except ftplib.error_perm, resp:
            if str(resp) == "550 No files found":
                print "Empty Directory"
            else:
                pass

    def file_upload(self, file_name, dest_dir, server, u_name, password, old_files):
        status = 0

        ftp = self.login_to_ftp_server(server, u_name, password)

        try:
            try:
                # Change directory in ftp Server
		ftp.cwd(dest_dir)
		f = open(file_name, 'rb')
		ftp.storbinary('STOR %s' % file_name, f)  # Transfer the file to destination
		f.close()
		status = 1

		# Delete 7Days old files
		if old_files: self.remove_old_files(ftp)
            finally:
                # Quit from ftp Server
                ftp.quit()
        except:
            print traceback.print_exc()

        return status
    """
    def main(self):
        os.system('mysqldump -u root nextpulse --password=root > samp_one.sql')
	today = str(datetime.now().date())
	file_name = "nextpulse_databackup_%s.tar.gz" % today
	os.system('tar -czvf %s *.sql' %file_name)
    #status = self.file_upload(file_name, self.backup_path, self.server, self.user_name, self.password, 0)

if __name__ == '__main__':
    OBJ = BackupScript()
    OBJ.main()
