# -*- coding: utf-8 -*-

default_page_size = 66
bwprint_exe = ['wine',
               '/home/USER/.wine/drive_c/Program Files/Baan/Baan Windows/bin/bwprint.exe']

pdf_printer = '@ -p "Virtual PDF Printer" -c 2 -f 1 -t 9999999 -l 66 -m 4 -L -a 1 -r {0} -w 132 -s 9 -d P -B "PDFCREATOR"@"'
printer_output = '/var/spool/cups-pdf/USER/'

# windows settings
# bwprint_exe = ['C:\Program Files (x86)\Infor\BW\ERPLN\bin\bwprint.exe']
# printer_output = 'c:\Temp\pdf'
