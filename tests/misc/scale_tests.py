"""
Tests for the :mod:`fiftyone.utils.scale` module.

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import unittest

import eta.core.utils as etau

import fiftyone as fo
import fiftyone.zoo as foz
import fiftyone.utils.scale as fous


@unittest.skip("Must be run manually")
def test_scale_image():
    # Image dataset
    _dataset = foz.load_zoo_dataset(
        "bdd100k", split="validation", shuffle=True, max_samples=10
    )
    dataset = fo.Dataset()
    dataset.add_samples(_dataset.take(10))

    _test_scale_image(dataset)


@unittest.skip("Must be run manually")
def test_scale_video_objects():
    # Video dataset with objects
    dataset = foz.load_zoo_dataset("quickstart-video", max_samples=10)

    _test_scale_video(dataset)


@unittest.skip("Must be run manually")
def test_scale_video_events():
    # Video dataset with events
    dataset = fo.Dataset()

    events = [
        {"label": "sunny", "frames": [1, 10]},
        {"label": "cloudy", "frames": [11, 20]},
        {"label": "sunny", "frames": [21, 30]},
    ]

    sample = fo.Sample(filepath="/path/to/road.mp4")

    for event in events:
        label = event["label"]
        frames = event["frames"]
        for frame_number in range(frames[0], frames[1] + 1):
            sample.frames[frame_number]["weather"] = fo.Classification(
                label=label
            )

    dataset.add_sample(sample)

    _test_scale_video(dataset)


def _test_scale_image(dataset):
    scale_export_path = "/tmp/scale-image-export.json"
    scale_import_path = "/tmp/scale-image-import.json"
    scale_id_field = "scale_id"

    # Export labels in Scale format
    fous.export_to_scale(
        dataset, scale_export_path, label_prefix="",  # all fields
    )

    # Convert to Scale import format
    id_map = fous.convert_scale_export_to_import(
        scale_export_path, scale_import_path
    )

    for sample_id, task_id in id_map.items():
        sample = dataset[sample_id]
        sample[scale_id_field] = task_id
        sample.save()

    # Import labels from Scale
    fous.import_from_scale(
        dataset,
        scale_import_path,
        label_prefix="scale",
        scale_id_field=scale_id_field,
    )

    # Verify that we have two copies of the same labels
    session = fo.launch_app(dataset)
    session.wait()


def _test_scale_video(dataset):
    scale_export_dir = "/tmp/scale-video-export"
    scale_export_path = "/tmp/scale-video-export.json"
    scale_import_path = "/tmp/scale-video-import.json"
    scale_id_field = "scale_id"

    etau.ensure_empty_dir(scale_export_dir)

    # Export labels in Scale format
    fous.export_to_scale(
        dataset,
        scale_export_path,
        video_labels_dir=scale_export_dir,
        video_playback=True,  # try both `True` and `False` here
        frame_labels_prefix="",  # all frame fields
    )

    # Convert to Scale import format
    id_map = fous.convert_scale_export_to_import(
        scale_export_path, scale_import_path
    )

    for sample_id, task_id in id_map.items():
        sample = dataset[sample_id]
        sample[scale_id_field] = task_id
        sample.save()

    # Import labels from Scale
    fous.import_from_scale(
        dataset,
        scale_import_path,
        label_prefix="scale",
        scale_id_field=scale_id_field,
    )

    # Verify that we have two copies of the same labels
    session = fo.launch_app(dataset)
    session.wait()


if __name__ == "__main__":
    fo.config.show_progress_bars = True
    unittest.main(verbosity=2)
