import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SegmentRecord:
    segment_id: str
    path: Path
    stream_start: float
    stream_end: float
    duration: float
    size: int


class SegmentStorage:
    def __init__(
        self,
        segment_dir: str,
        retention_seconds: float = 60
    ):
        self.segment_dir = Path(segment_dir)
        self.manifest_path = self.segment_dir / "segments.csv"
        self.retention_seconds = retention_seconds

        self.segments: dict[str, SegmentRecord] = {}
        self.protected_segments: set[str] = set()

        if retention_seconds <= 0:
            raise ValueError("Retention duration must be positive.")

    def refresh(self) -> list[SegmentRecord]:
        """ Load completed segments listed in the FFmpeg manifest. """

        if not self.manifest_path.is_file():
            return self.get_segments()

        with self.manifest_path.open(
            "r",
            newline="",
            encoding="utf-8"
        ) as manifest:
            reader = csv.reader(manifest)

            for row in reader:
                if len(row) < 3:
                    continue

                filename, start, end = row[:3]

                try:
                    stream_start = float(start)
                    stream_end = float(end)
                except ValueError:
                    continue

                if stream_end < stream_start:
                    continue

                segment_path = Path(filename)

                if not segment_path.is_absolute():
                    if not segment_path.is_file():
                        segment_path = self.segment_dir / segment_path.name

                segment_path = segment_path.resolve()

                # Never manage files outside the segment directory
                if segment_path.parent != self.segment_dir.resolve():
                    continue

                if not segment_path.is_file():
                    continue

                segment_id = segment_path.stem

                self.segments[segment_id] = SegmentRecord(
                    segment_id=segment_id,
                    path=segment_path,
                    stream_start=stream_start,
                    stream_end=stream_end,
                    duration=stream_end - stream_start,
                    size=segment_path.stat().st_size
                )

        return self.get_segments()

    def get_segments(self) -> list[SegmentRecord]:
        """ Return known segments in chronological order """

        return sorted(
            self.segments.values(),
            key=lambda segment: segment.stream_start
        )

    def protect_range(
        self,
        start_time: float,
        end_time: float
    ) -> list[SegmentRecord]:
        """Protect segments overlapping a requested time range."""

        if end_time < start_time:
            raise ValueError("End time cannot be before start time.")

        selected = []

        for segment in self.get_segments():
            overlaps = (
                segment.stream_end >= start_time
                and segment.stream_start <= end_time
            )

            if overlaps:
                self.protected_segments.add(segment.segment_id)
                selected.append(segment)

        return selected

    def release(self, segment_ids: list[str]):
        """Release segments after their clips have been generated."""

        for segment_id in segment_ids:
            self.protected_segments.discard(segment_id)

    def prune(self, current_stream_time: float | None = None) -> list[str]:
        """Delete expired segments unless they are protected."""

        if current_stream_time is None:
            if not self.segments:
                return []

            current_stream_time = max(
                segment.stream_end
                for segment in self.segments.values()
            )

        cutoff = current_stream_time - self.retention_seconds
        deleted = []

        for segment_id, segment in list(self.segments.items()):
            expired = segment.stream_end < cutoff
            protected = segment_id in self.protected_segments

            if expired and not protected:
                segment.path.unlink(missing_ok=True)
                del self.segments[segment_id]
                deleted.append(segment_id)

        return deleted
