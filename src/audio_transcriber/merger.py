"""
Transcription merging module for combining segment outputs.
"""

import json
import logging
from typing import List

logger = logging.getLogger(__name__)


class TranscriptionMerger:
    """
    Handles merging of transcribed segments with intelligent overlap removal.
    """

    def merge(self, transcriptions: List[str], response_format: str = "text") -> str:
        """
        Merge transcribed segments based on output format.

        Args:
            transcriptions: List of transcription strings
            response_format: Output format (text, json, srt, vtt, verbose_json)

        Returns:
            Merged transcription string

        Raises:
            ValueError: If response_format is unsupported
        """
        if not transcriptions:
            return ""

        if response_format == "text":
            return self._merge_text(transcriptions)
        elif response_format in ["json", "verbose_json"]:
            return self._merge_json(transcriptions)
        elif response_format == "srt":
            return self._merge_srt(transcriptions)
        elif response_format == "vtt":
            return self._merge_vtt(transcriptions)
        else:
            # Fallback: simple concatenation
            logger.warning(f"Unknown format '{response_format}', using simple merge")
            return "\n".join(t for t in transcriptions if t)

    def _merge_text(self, transcriptions: List[str]) -> str:
        """
        Merge plain text transcriptions with overlap deduplication.

        This uses a simple heuristic: if the first sentence of a segment
        matches the last sentence of the accumulated text, skip it to
        avoid duplication from overlapping segments.

        Args:
            transcriptions: List of text transcriptions

        Returns:
            Merged text
        """
        if not transcriptions:
            return ""

        if len(transcriptions) == 1:
            return transcriptions[0].strip()

        merged_parts = [transcriptions[0].strip()]

        for i in range(1, len(transcriptions)):
            current = transcriptions[i].strip()
            if not current:
                continue

            # Split into sentences for overlap detection
            current_sentences = self._split_sentences(current)
            merged_text = " ".join(merged_parts)
            merged_sentences = self._split_sentences(merged_text)

            # Check for overlap between last merged sentence and first current sentence
            if merged_sentences and current_sentences:
                last_merged = merged_sentences[-1].strip().lower()
                first_current = current_sentences[0].strip().lower()

                # If there's significant overlap, skip the first sentence
                if last_merged and first_current and self._sentences_similar(
                    last_merged, first_current
                ):
                    # Skip first sentence, add the rest
                    remaining = " ".join(current_sentences[1:])
                    if remaining.strip():
                        merged_parts.append(remaining.strip())
                    continue

            merged_parts.append(current)

        return " ".join(merged_parts)

    def _merge_json(self, transcriptions: List[str]) -> str:
        """
        Merge JSON transcriptions.

        Args:
            transcriptions: List of JSON transcription strings

        Returns:
            Combined JSON string
        """
        all_data = []

        for trans in transcriptions:
            if not trans.strip():
                continue

            try:
                data = json.loads(trans)
                all_data.append(data)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON segment: {e}")
                continue

        if not all_data:
            return json.dumps({"segments": [], "text": ""})

        # Combine all segments
        combined = {
            "text": " ".join(str(d.get("text", "")) for d in all_data),
            "segments": all_data,
            "language": all_data[0].get("language") if all_data else None,
        }

        return json.dumps(combined, indent=2, ensure_ascii=False)

    def _merge_srt(self, transcriptions: List[str]) -> str:
        """
        Merge SRT subtitle transcriptions with timestamp adjustment.

        Args:
            transcriptions: List of SRT transcription strings

        Returns:
            Combined SRT string
        """
        if not transcriptions:
            return ""

        # For now, simple concatenation
        # Full implementation would parse and adjust timestamps
        merged_entries = []
        entry_number = 1

        for trans in transcriptions:
            if not trans.strip():
                continue

            # Simple merge - each segment should have correct timestamps already
            entries = trans.strip().split("\n\n")
            for entry in entries:
                if entry.strip():
                    # Renumber entries
                    lines = entry.split("\n")
                    if len(lines) >= 3:
                        lines[0] = str(entry_number)
                        merged_entries.append("\n".join(lines))
                        entry_number += 1

        return "\n\n".join(merged_entries)

    def _merge_vtt(self, transcriptions: List[str]) -> str:
        """
        Merge VTT subtitle transcriptions.

        Args:
            transcriptions: List of VTT transcription strings

        Returns:
            Combined VTT string
        """
        if not transcriptions:
            return "WEBVTT\n\n"

        merged = ["WEBVTT"]

        for trans in transcriptions:
            if not trans.strip():
                continue

            # Remove WEBVTT header and merge
            lines = trans.strip().split("\n")
            content = [line for line in lines if line.strip() != "WEBVTT"]
            merged.extend(content)

        return "\n".join(merged)

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """
        Split text into sentences (simple implementation).

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting on common terminators
        import re

        sentences = re.split(r"[.!?]+\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def _sentences_similar(sent1: str, sent2: str, threshold: float = 0.8) -> bool:
        """
        Check if two sentences are similar (for overlap detection).

        Args:
            sent1: First sentence
            sent2: Second sentence
            threshold: Similarity threshold (0-1)

        Returns:
            True if sentences are similar enough
        """
        # Simple word-based similarity
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())

        if not words1 or not words2:
            return False

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold
