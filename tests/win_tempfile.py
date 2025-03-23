# pulled from https://stackoverflow.com/questions/2549384/how-do-i-create-a-named-temporary-file-on-windows-in-python

import os
from collections.abc import Generator
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import IO


@contextmanager
def NamedTempFile(**kwargs) -> Generator[IO, None, None]:
    """
    This is a workaround for creating temporary files on Windows,
    as regular `with TemporaryFile() as tmp` not working properly.
    """
    tmp = NamedTemporaryFile(delete=False, **kwargs)
    try:
        yield tmp
        tmp.close()
    finally:
        # remove temp file before exiting
        os.unlink(tmp.name)
