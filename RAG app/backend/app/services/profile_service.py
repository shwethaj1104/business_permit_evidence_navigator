from app.core.errors import AppError
from app.core.logging import logged_operation
from app.models.domain import PROFILE


class ProfileService:
    """Validate both tabs against the same supported profile."""

    def list(self):
        # Return only implemented profile combinations.
        return [PROFILE]

    @logged_operation("profile.validate")
    def require(self, profile_id):
        # Reject unsupported scopes before any retrieval or paid request.
        if profile_id != PROFILE.id:
            raise AppError("This business profile is not supported yet.", 422)
        return PROFILE
