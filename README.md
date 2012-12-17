BaanPrint
=========

### About BaanPrint

BaanPrint does exactly two things:

#### 1

Convert a Baan standard report into a PDF. Optionally merging a PDF into every page. (E.g. to add your company logo)

#### 2

Execute a custom python script that processes the report. This can be used for all sorts of things.
E.g. Automatically send purchase orders to suppliers, invoices to customers, archive PDF files, and much more!

### Motivation

There are different ways to accomplish PDF printing in Erp LN. The main motivation for BaanPrint was to get PDFs that look absolutely identical to reports that are printed using regular Windows printers.
This is why BaanPrint utilizes bwprint.exe (see architecture overview) to create the PDF file using a virtual PDF printer.

Generating Postscript or RTF files from Baan/Erp LN and then convert these to PDF would result in a loss of the font settings.


### Architecture Overview

Here is a little overview how it works:

![baanprinting.png][baanprinting]

### Installation & Requirements

BaanPrint is targeted towards Windows Systems as it utilises bwprint.exe for its PDF conversion functionality.
Although it is possible to get it working on Linux (using wine for bwprint.exe)

BaanPrint requires either Python 2.7 or Python >=3.2 and some Python modules (listed in requirements.txt).
Currently using Python 2.7 is recommended.

For instructions on how to install Python, please refer to [this blog post][installinstructions].
Following step 1 and 2 is sufficient to get BaanPrint working.

Usually you can install Python modules using PIP.

    #> pip install -r requirements.txt

But in this case there are two edge cases depending on whether you are using Python 2.7 or Python 3.2

#### Python 2.7

The current Yapsy package in the Python Package Index is for python3. So using

    #> pip install Yapsy 

won't work. Please use

    #> pip install  http://sourceforge.net/projects/yapsy/files/Yapsy-1.9/Yapsy-1.9.tar.gz/download

instead.

#### Python 3.2

BaanPrint requires the pyPdf package.  
For Python 3.2 it is currently only available in a branch on [Github][github]. You can install that using

    #> pip install git+git://github.com/mfenniak/pyPdf.git@py3

#### Virtual PDF Printer

To generate the PDFs, a virtual PDF Printer ([PdfCreator][pdfcreator] being recommended) is required. The PDF Printer should be installed on the Infor ERP LN system and configured to use auto-save.

In addition the `config.py` has to be adjusted for two options:

 * The name of the printer
 * The location where the printer is auto-saving the PDFs.

#### Erp LN Print Device & Session Script

A development license for ERP LN is required to create a custom 3G session script within ERP LN. This script is included in BaanPrint [bwprint.bc][bwprintbc].

In addition a print device has to be added using the `ttaad3500m000` session.

The 4GL Program parameter should be filled with the name of the session created earlier.
The argument field has to be filled with either

 * `convert "{0}" "{1}" {2} {3}`
 * `convert -t "c:\path\to\template.pdf" "{0}" "{1}"`
 * `handle "{0}" {1} {2} {3}`

depending on what the print device should do. In case of `convert` the path field should be filled with the file name the PDF is going to have once transfered to the client/user. E.g. `fileout.pdf`.

### Development

BaanPrint is licensed under the MIT license. So everyone is free to use it or develop on it.

### Alternatives

BaanPrint isn't a full-featured reporting system.
There are already enough existing solutions. For example BIRT or MS Reporting Services both of which
are integrated into Erp LN.

And there are also very powerful solutions like [StreamServe][streamserve].

[streamserve]: http://www.streamserve.com/
[baanprinting]: https://github.com/mfussenegger/BaanPrint/raw/master/docs/baanprinting.png
[bwprintbc]: https://github.com/mfussenegger/BaanPrint/raw/master/bwprint.bc
[pdfcreator]: http://sourceforge.net/projects/pdfcreator/
[github]: http://github.com
[installinstructions]: https://zignar.net/2012/06/17/install-python-on-windows/
