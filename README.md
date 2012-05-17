BaanPrint
=========

### What BaanPrint isn't

BaanPrint isn't a full-featured reporting system.
There are already enough existing solutions. For example BIRT or MS Reporting Services both of which
are integrated into Erp LN.

And there are also very powerful solutions like [StreamServe][streamserve].

### What it is

A very simple output management framework for Infor ERP LN written in python.

It can be used to do two things:

#### 1

Convert a Baan standard report into a PDF. Optionally merging a PDF into every page. (E.g. to add your company logo)

#### 2

Execute a custom python script that processes the report. This can be used for all sorts of things.
Automatically send purchase orders to suppliers, invoices to customers, archive PDF files, and much more!

Here is a little overview how it works:

![baanprinting.png][baanprinting]


### Requirements & Development

BaanPrint is licensed under the MIT license. So everyone is free to use it or develop on it.


BaanPrint is targeted towards Windows Systems as it utilises bwprint.exe for its PDF conversion functionality.

As it is written in Python, Python3 and the libraries mentioned in requirements.txt are required to use it.
These dependencies can easily be installed using PIP.

    #> pip install -r requirements.txt

To generate the PDF files, a virtual PDF Printer ([PdfCreator][pdfcreator] being recommended) is required.
The `config.py` file has to be adjusted to point to the appropriate printer.

[streamserve]: http://www.streamserve.com/
[baanprinting]: https://github.com/mfussenegger/BaanPrint/raw/master/docs/baanprinting.png
[pdfcreator]: http://sourceforge.net/projects/pdfcreator/
