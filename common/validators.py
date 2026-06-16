from datetime import date
from rest_framework.exceptions import ValidationError


def validate_user_age_from_token(request):
    birthdate = request.auth.get("birthdate") if request.auth else None

    if not birthdate:
        raise ValidationError("Birthdate is required in the token to validate age.")

    birthdate = date.fromisoformat(birthdate)

    today = date.today()
    age = today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )

    if age < 18:
        raise ValidationError("User must be at least 18 years old to access this resource.")