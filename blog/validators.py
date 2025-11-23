from django.core.exceptions import ValidationError 
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible

@deconstructible
class FileSizeValidator:
    def __init__(self, max_size_mb=5):
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def __call__(self, value):
        if value.size > self.max_size_bytes:
            raise ValidationError(
                f'Размер файла не должен превышать {self.max_size_mb} МБ. '
                f'Текущий размер: {value.size / (1024 * 1024):.2f} МБ.'
            )
        
    def __eq__(self, other):
        return isinstance(other, FileSizeValidator) and self.max_size_mb == other.max_size_mb
    
def validate_image_extension(value):
    validator = FileExtensionValidator(
        allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
        message='Поддерживаются только форматы: JPG, JPEG, PNG, WEBP'
    )
    return validator(value)