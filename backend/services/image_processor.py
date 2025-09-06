"""
Image processing service for handling portrait uploads and validation.
"""
import io
import logging

from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Service for processing and validating uploaded images."""

    async def validate_image(self, file_data: bytes) -> bool:
        """
        Validate that the file data is a valid image.

        Args:
            file_data: Raw bytes of the uploaded file

        Returns:
            True if valid image, False otherwise
        """
        try:
            image = Image.open(io.BytesIO(file_data))
            image.verify()
            return True
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False

    async def resize_image(
        self,
        file_data: bytes,
        max_size: tuple[int, int] = (1024, 1024)
    ) -> bytes:
        """
        Resize image if it exceeds maximum dimensions.

        Args:
            file_data: Raw bytes of the uploaded file
            max_size: Maximum width and height tuple

        Returns:
            Processed image bytes
        """
        try:
            image = Image.open(io.BytesIO(file_data))

            # Convert RGBA to RGB if necessary for JPEG compatibility
            if image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = rgb_image  # type: ignore[assignment]

            # Resize if needed
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='PNG', optimize=True)
            output.seek(0)
            return output.read()

        except Exception as e:
            logger.error(f"Image resizing failed: {e}")
            # Return original if processing fails
            return file_data


# Global service instance
image_processor = ImageProcessor()
