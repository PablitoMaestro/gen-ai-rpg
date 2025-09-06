from PIL import Image
from io import BytesIO
import base64
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageProcessorService:
    """Service for image processing and manipulation."""
    
    @staticmethod
    async def resize_image(
        image_bytes: bytes,
        max_size: Tuple[int, int] = (1024, 1024)
    ) -> bytes:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image_bytes: Original image bytes
            max_size: Maximum dimensions (width, height)
            
        Returns:
            Resized image bytes
        """
        try:
            img = Image.open(BytesIO(image_bytes))
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            output = BytesIO()
            img.save(output, format='PNG', optimize=True)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            return image_bytes
    
    @staticmethod
    async def composite_images(
        background_bytes: bytes,
        foreground_bytes: bytes,
        position: Optional[Tuple[int, int]] = None
    ) -> bytes:
        """
        Composite two images together.
        
        Args:
            background_bytes: Background image bytes
            foreground_bytes: Foreground image bytes
            position: Position for foreground image (x, y)
            
        Returns:
            Composited image bytes
        """
        try:
            background = Image.open(BytesIO(background_bytes))
            foreground = Image.open(BytesIO(foreground_bytes))
            
            # Convert to RGBA for transparency support
            if background.mode != 'RGBA':
                background = background.convert('RGBA')
            if foreground.mode != 'RGBA':
                foreground = foreground.convert('RGBA')
            
            # Default position: center
            if position is None:
                x = (background.width - foreground.width) // 2
                y = (background.height - foreground.height) // 2
                position = (x, y)
            
            # Composite images
            background.paste(foreground, position, foreground)
            
            output = BytesIO()
            background.save(output, format='PNG')
            return output.getvalue()
        except Exception as e:
            logger.error(f"Failed to composite images: {e}")
            return background_bytes
    
    @staticmethod
    def image_to_base64(image_bytes: bytes) -> str:
        """Convert image bytes to base64 string."""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    @staticmethod
    def base64_to_image(base64_string: str) -> bytes:
        """Convert base64 string to image bytes."""
        return base64.b64decode(base64_string)
    
    @staticmethod
    async def validate_image(image_bytes: bytes) -> bool:
        """
        Validate that bytes represent a valid image.
        
        Args:
            image_bytes: Image bytes to validate
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            img = Image.open(BytesIO(image_bytes))
            img.verify()
            return True
        except Exception:
            return False


# Singleton instance
image_processor = ImageProcessorService()