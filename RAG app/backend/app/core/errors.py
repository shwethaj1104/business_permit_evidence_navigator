class AppError(Exception):
    """Carry a safe error message across API and worker boundaries."""

    def __init__(self, message: str, status: int = 400):
        # Keep provider details and credentials out of public responses.
        super().__init__(message)
        self.message = message
        self.status = status
