import gridfs


class SourceFiles:
    """Store original source snapshots in the same MongoDB database."""

    def __init__(self, db):
        # Bind GridFS to this process's database connection.
        self.bucket = gridfs.GridFS(db)

    def save(self, version_id, content, content_type):
        # Reuse the same file ID when an interrupted source is processed again.
        if not self.bucket.exists(version_id):
            self.bucket.put(content, _id=version_id, filename=version_id, contentType=content_type)
        return version_id
