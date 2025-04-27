import re
import os
import logging
import magic
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

logger = logging.getLogger("security")


def sanitize_user_input(content):
    """
    Sanitize user input to remove potentially malicious content.

    Args:
        content (str): The user input to sanitize

    Returns:
        str: Sanitized content
    """
    if not content:
        return content

    # Remove HTML tags
    sanitized = strip_tags(content)

    # Remove any script-like content
    sanitized = re.sub(r"javascript:", "", sanitized, flags=re.IGNORECASE)

    return sanitized


def validate_file_type(file_obj, allowed_types=None):
    """
    Validate that a file is of an allowed type by checking its MIME type.

    Args:
        file_obj: The uploaded file object
        allowed_types (list): List of allowed MIME types. If None, defaults to images, PDFs and documents.

    Returns:
        bool: True if file is valid, False otherwise

    Raises:
        ValidationError: If the file type is not allowed
    """
    if not file_obj:
        return True

    if allowed_types is None:
        allowed_types = [
            # Images
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            # Documents
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
        ]

    # Read the first few bytes to determine file type
    file_header = file_obj.read(2048)
    file_obj.seek(0)  # Reset file pointer

    # Use python-magic to get the MIME type
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_header)

    if file_type not in allowed_types:
        logger.warning(
            f"Blocked upload of file with disallowed type: {file_type}, "
            f"filename: {file_obj.name}"
        )
        raise ValidationError(
            f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )

    return True


def validate_image_file(file_obj):
    """
    Validate that a file is an image.

    Args:
        file_obj: The uploaded file object

    Returns:
        bool: True if file is a valid image

    Raises:
        ValidationError: If the file is not a valid image
    """
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    return validate_file_type(file_obj, allowed_types)


def sanitize_filename(filename):
    """
    Sanitize a filename to remove potentially dangerous characters.

    Args:
        filename (str): The filename to sanitize

    Returns:
        str: Sanitized filename
    """
    if not filename:
        return filename

    # Get base filename and extension
    base, ext = os.path.splitext(filename)

    # Remove or replace dangerous characters
    base = re.sub(r"[^\w\-\.]", "_", base)

    # Limit length
    if len(base) > 200:
        base = base[:200]

    return base + ext
