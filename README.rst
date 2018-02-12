Create a difference on two RFC XML files
========================================

This program takes two XML files containing SVG or RFC documents and creates an HTML
file which shows the differences between the two documents.

The `RFC Editor`_ is in the process of changing the canonical input format of
Internet-Draft_ and RFC_ documents.  Further information on the process can be found
on the RFC Editor at the `RFC Editor`_ site.

.. _Internet-Draft: https://en.wikipedia.org/wiki/Internet_Draft
.. _RFC: https://en.wikipedia.org/wiki/Request_for_Comments
.. _RFC 7996 bis: https://datatracker.ietf.org/doc/draft-7996-bis
.. _RFC Editor: https://www.rfc-editor.org

Usage
=====

xmldiff accepts a pair of XML documents as input and outputs an HTML document.

**Basic Usage**: ``xmldiff [options] SOURCE1 SOURCE2``

**Options**
   The following parameters affect how xmldiff behaves, however none are required.

    ===============  ======================= ==================================================
    Short            Long                    Description
    ===============  ======================= ==================================================
    ``-C``           ``--clear-cache``       purge the cache and exit
    ``-h``           ``--help``              show the help message and exit
    ``-N``           ``--no-network``        don't use the network to resolve references
    ``-q``           ``--quiet``             dont print anything
    ``-v``           ``--verbose``           print extra information
    ``-V``           ``--version``           display the version number and exit
    ``-X``           ``--no-xinclude``       don't resolve xi:include elements

    ``-o FILENAME``  ``--out=FILENAME``      specify an output filename
    ===============  ======================= ==================================================

Dependencies
============

xmldiff depends on the following packages:

* lxml_ *(>= 4.1.1)*
* requests_ *(>= 2.5.0)*
* `rfctools_common`_ *(>= 0.1.0)*
* 'cffi_ *(>= 1.0.0)*

.. _lxml: http://lxml.de
.. _requests: http://docs.python-requests.org
.. _rfctools_common: https://pypi.python.org/pypi/pip
.. _cffi: https://pypi.python.org/pypi/pip

