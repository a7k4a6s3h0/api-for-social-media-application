from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Custom validator to check video file size
def validate_video_size(value):
    # Maximum allowed file size in bytes (40MB)
    max_size = 40 * 1024 * 1024

    if value.size > max_size:
        raise ValidationError(_('The video file size should not exceed 40MB.'))


# Custom validator to check image file size
def validate_image_size(value):
    # Maximum allowed file size in bytes (40MB)
    max_size = 40 * 1024 * 1024
    
    if value.size > max_size:
        raise ValidationError(_('The image file size should not exceed 40MB.'))
