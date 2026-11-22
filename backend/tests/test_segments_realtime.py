from app.video.segmenter import VideoSegmenter
from app.video.storage import SegmentStorage
import time

# split the realtime video in segments
segmenter = VideoSegmenter(
    source="storage/sample/sample.mp4",
    output_dir="storage/buffer/segments",
    segment_duration=2,
    realtime=True
)

# loading the segments
storage = SegmentStorage(
    segment_dir="storage/buffer/segments",
    retention_seconds=6
)

try:
    segmenter.start()
    print("LIve simulation has started")

    while segmenter.is_running():

        #load newly completed segments
        segments = storage.refresh()

        if segments:
            latest_time = max(segment.stream_end for segment in segments)

            deleted = storage.prune(latest_time)

            print(
                f"Stream time : {latest_time:.2f}s | Retained : {len(storage.get_segments())} | Deleted : {len(deleted)}"
            )
        time.sleep(1)
    segmenter.wait()

    storage.refresh()
    storage.prune()
    print("Live Simulation Finished")

finally:
    if segmenter.is_running():
        segmenter.stop()