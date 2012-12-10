from apiclient.http import MediaUpload

class MediaInMemoryUpload(MediaUpload):
    """MediaUpload for a chunk of bytes.

    Construct a MediaFileUpload and pass as the media_body parameter of the
    method. For example, if we had a service that allowed plain text:
    """

    def __init__(self, body, mimetype='application/octet-stream',
                             chunksize=256 * 1024, resumable=False):
        """Create a new MediaBytesUpload.

        Args:
            body: string, Bytes of body content.
            mimetype: string, Mime-type of the file or default of
                'application/octet-stream'.
            chunksize: int, File will be uploaded in chunks of this many bytes. Only
                used if resumable=True.
            resumable: bool, True if this is a resumable upload. False means upload
                in a single request.
        """
        self._body = body
        self._mimetype = mimetype
        self._resumable = resumable
        self._chunksize = chunksize

    def chunksize(self):
        """Chunk size for resumable uploads.

        Returns:
            Chunk size in bytes.
        """
        return self._chunksize

    def mimetype(self):
        """Mime type of the body.

        Returns:
            Mime type.
        """
        return self._mimetype

    def size(self):
        """Size of upload.

        Returns:
            Size of the body.
        """
        return len(self._body)

    def resumable(self):
        """Whether this upload is resumable.

        Returns:
            True if resumable upload or False.
        """
        return self._resumable

    def getbytes(self, begin, length):
        """Get bytes from the media.

        Args:
            begin: int, offset from beginning of file.
            length: int, number of bytes to read, starting at begin.

        Returns:
            A string of bytes read. May be shorter than length if EOF was reached
            first.
        """
        return self._body[begin:begin + length]
    