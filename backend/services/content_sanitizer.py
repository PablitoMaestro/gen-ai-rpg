"""Content sanitizer for image generation to avoid Gemini's content filters."""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

class ContentSanitizer:
    """Sanitizes content to avoid rejection by Gemini Flash image generation."""

    # Mapping of problematic words/phrases to safe alternatives
    VIOLENCE_REPLACEMENTS: dict[str, str] = {
        # Blood and gore
        r'\bblood\b': 'red marks',
        r'\bbloodstain\w*\b': 'red marks',
        r'\bbloody\b': 'marked',
        r'\bbleeding\b': 'wounded',
        r'\bgore\b': 'debris',
        r'\bgory\b': 'messy',
        r'\bcorpse\b': 'fallen figure',
        r'\bcorpses\b': 'fallen figures',
        r'\bdead body\b': 'still figure',
        r'\bdead bodies\b': 'still figures',
        r'\brot\b': 'decay',
        r'\brotting\b': 'weathered',
        r'\bpus\b': 'fluid',

        # Violence and weapons
        r'\bmassacre\b': 'conflict',
        r'\bmurder\b': 'conflict',
        r'\btorture\b': 'ordeal',
        r'\bbrutally\b': 'harshly',
        r'\bbrutal\b': 'harsh',
        r'\bsavage\b': 'wild',
        r'\bvicious\b': 'fierce',
        r'\bstab\b': 'strike',
        r'\bstabbed\b': 'struck',
        r'\bstabbing\b': 'striking',
        r'\bslash\b': 'cut',
        r'\bslashing\b': 'cutting',
        r'\bslaughter\b': 'defeat',
        r'\bkill\b': 'defeat',
        r'\bkilling\b': 'defeating',
        r'\bdismember\b': 'separate',
        r'\bdecapitat\b': 'remove',

        # Disturbing/ugly descriptors
        r'\bugly\b': 'weathered',
        r'\bhideous\b': 'unusual',
        r'\bgrotesk\b': 'strange',
        r'\bhorrible\b': 'unsettling',
        r'\bhorrific\b': 'mysterious',
        r'\bterrifying\b': 'imposing',
        r'\bterrible\b': 'challenging',
        r'\bnightmarish\b': 'dreamlike',
        r'\bghastly\b': 'pale',
        r'\bmonstrous\b': 'large',
        r'\brepulsive\b': 'unusual',
        r'\brepugnant\b': 'off-putting',
        r'\brevolting\b': 'strange',

        # Death and doom
        r'\bdeath\b': 'end',
        r'\bdie\b': 'fall',
        r'\bdying\b': 'fading',
        r'\bdoom\b': 'fate',
        r'\bdoomed\b': 'challenged',
        r'\bperish\b': 'fade',
        r'\bperishing\b': 'fading',
        r'\bdemise\b': 'end',

        # Dark magic and curses
        r'\bcursed\b': 'enchanted',
        r'\bdamned\b': 'troubled',
        r'\bpossessed\b': 'influenced',
        r'\bhaunted\b': 'mysterious',
        r'\bnecromancy\b': 'dark magic',
        r'\bzombie\b': 'undead figure',
        r'\bzombies\b': 'undead figures',
        r'\bskeleton\b': 'bone figure',
        r'\bskeletons\b': 'bone figures',

        # Tragedy and suffering
        r'\btragedy\b': 'misfortune',
        r'\bsuffering\b': 'hardship',
        r'\bagony\b': 'difficulty',
        r'\banguish\b': 'worry',
        r'\btorment\b': 'trouble',
        r'\bmisery\b': 'sadness',
        r'\bpain\b': 'discomfort',
        r'\bpainful\b': 'difficult',

        # War and conflict
        r'\bwar\b': 'conflict',
        r'\bbattle\b': 'encounter',
        r'\bfight\b': 'challenge',
        r'\bcombat\b': 'contest',
        r'\battack\b': 'approach',
        r'\bassault\b': 'confrontation',
        r'\binvasion\b': 'arrival',
        r'\braiding\b': 'visiting',
        r'\bsiege\b': 'blockade',
    }

    # Additional patterns for extreme content
    EXTREME_PATTERNS = [
        r'\bexecutio\w+',  # execution, executing, etc.
        r'\btortur\w+',   # torture, torturing, etc.
        r'\bmutilat\w+',  # mutilate, mutilating, etc.
        r'\bdisembow\w+', # disembowel, etc.
        r'\bcannibal\w+', # cannibal, cannibalism, etc.
        r'\bsuicid\w+',   # suicide, suicidal, etc.
        r'\bhomicid\w+',  # homicide, etc.
        r'\bgenocid\w+',  # genocide, etc.
    ]

    def __init__(self) -> None:
        """Initialize the content sanitizer."""
        # Compile regex patterns for performance
        self.compiled_replacements = {
            re.compile(pattern, re.IGNORECASE): replacement
            for pattern, replacement in self.VIOLENCE_REPLACEMENTS.items()
        }

        self.extreme_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.EXTREME_PATTERNS
        ]

    def sanitize_for_image_generation(self, text: str) -> str:
        """
        Sanitize text for image generation while preserving the core meaning.

        Args:
            text: Original text that may contain content filter triggers

        Returns:
            Sanitized text safe for image generation
        """
        if not text:
            return text

        sanitized = text
        original_text = text  # Keep for logging

        # Apply word replacements
        for pattern, replacement in self.compiled_replacements.items():
            sanitized = pattern.sub(replacement, sanitized)

        # Remove extreme content patterns
        for pattern in self.extreme_patterns:
            if pattern.search(sanitized):
                # Replace entire phrases containing extreme patterns
                sanitized = pattern.sub('[intense scene]', sanitized)
                logger.warning("Removed extreme content pattern from image prompt")

        # Additional cleanup
        sanitized = self._clean_up_text(sanitized)

        # Log if significant changes were made
        if sanitized != original_text:
            logger.info(f"Sanitized image prompt: '{original_text[:50]}...' → '{sanitized[:50]}...'")

        return sanitized

    def _clean_up_text(self, text: str) -> str:
        """Perform final cleanup on sanitized text."""
        # Remove excessive adjectives that might still trigger filters
        excessive_adj = [
            'extremely', 'terribly', 'horribly', 'awfully', 'dreadfully',
            'frighteningly', 'shockingly', 'disturbingly', 'sickeningly'
        ]

        for adj in excessive_adj:
            text = re.sub(rf'\b{adj}\b', 'very', text, flags=re.IGNORECASE)

        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Ensure the text still makes sense
        text = text.strip()

        return text

    def is_content_safe_for_images(self, text: str) -> bool:
        """
        Check if content is likely safe for image generation.

        Args:
            text: Text to check

        Returns:
            True if content appears safe, False if it needs sanitization
        """
        if not text:
            return True

        # Check for extreme patterns first
        for pattern in self.extreme_patterns:
            if pattern.search(text):
                return False

        # Check for violence/gore terms
        violence_words = 0
        for pattern in self.compiled_replacements.keys():
            matches = pattern.findall(text)
            violence_words += len(matches)

        # If more than 2 violent terms, consider unsafe
        return violence_words <= 2

    def get_sanitization_report(self, original: str, sanitized: str) -> dict[str, Any]:
        """
        Generate a report of changes made during sanitization.

        Args:
            original: Original text
            sanitized: Sanitized text

        Returns:
            Report dictionary with changes made
        """
        changes = []

        # Find specific replacements made
        for pattern, replacement in self.compiled_replacements.items():
            matches = pattern.findall(original)
            if matches:
                changes.append({
                    'type': 'replacement',
                    'original_terms': matches,
                    'replacement': replacement,
                    'count': len(matches)
                })

        return {
            'original_length': len(original),
            'sanitized_length': len(sanitized),
            'changes_made': len(changes),
            'changes': changes,
            'is_safe': self.is_content_safe_for_images(sanitized)
        }


# Singleton instance
content_sanitizer = ContentSanitizer()
