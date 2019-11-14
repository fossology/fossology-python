=======
Logging
=======

This module uses the standard Python logging module to generate meaningful logs.

To retrieve the logs, use this snippet:

.. code-block:: python

    logger = logging.getLogger("fossology")
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)

Refer to the official documentation of the `logging module <https://docs.python.org/3/howto/logging.html>`_ for further details about the possible
configuration options.
