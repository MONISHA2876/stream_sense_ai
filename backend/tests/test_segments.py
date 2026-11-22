from app.video.segmenter import VideoSegmenter
from app.video.storage import SegmentStorage

# split the sample video in segments
segmenter = VideoSegmenter(
    source="storage/sample/sample.mp4",
    output_dir="storage/buffer/segments",
    segment_duration=2,
    realtime=False
)

try:
    pid = segmenter.start()
    print("Segmenter stared . PID : ", pid)

    segmenter.wait()
    print("Segmentation Completed")

finally:
    if segmenter.is_running():
        segmenter.stop()

# loading the segments
storage = SegmentStorage(
    segment_dir="storage/buffer/segments",
    retention_seconds=6
)

segments = storage.refresh()

print("\n Generated segments :")

for segment in segments:
    print(f" ID: {segment.segment_id}     {segment.stream_start:.2f}s - {segment.stream_end:.2f}s   Size:{segment.size} bytes" )

# protected range
protected = storage.protect_range(
    start_time=0,
    end_time=6
)

print("\n Protected Segments : ")
for segment in protected:
    print(segment.segment_id)

# remove the expired segments

deleted = storage.prune()
print("\nDeleted segments", deleted)

storage.release([segment.segment_id for segment in protected])

delete_after_release = storage.prune()

print("\n Remaining segments : ")
for segment in storage.get_segments():
    print(segment.segment_id, segment.duration)