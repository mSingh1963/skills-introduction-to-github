#!/usr/bin/env python3
"""
convert_mp4_to_photos.py

Extracts frames from an MP4 video file and saves them as image files.

Usage:
    python3 convert_mp4_to_photos.py <input.mp4> [output_dir] [--fps <rate>]

Arguments:
    input.mp4   Path to the source MP4 file.
    output_dir  Directory where extracted images will be saved (default: same
                directory as the input file, in a sub-folder named after the
                video).
    --fps       How many frames per second to capture (default: 1).  Use 0 to
                capture every single frame.

Examples:
    # Extract one frame per second into ./my_video/
    python3 convert_mp4_to_photos.py my_video.mp4

    # Extract two frames per second into /tmp/frames/
    python3 convert_mp4_to_photos.py my_video.mp4 /tmp/frames --fps 2

    # Extract every frame
    python3 convert_mp4_to_photos.py my_video.mp4 /tmp/frames --fps 0
"""

import argparse
import os
import sys

try:
    import cv2
except ImportError:
    print(
        "Error: opencv-python is required.\n"
        "Install dependencies with:  pip install -r requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


def convert(input_path: str, output_dir: str, fps: float) -> int:
    """Extract frames from *input_path* and write them to *output_dir*.

    Parameters
    ----------
    input_path:
        Path to the source MP4 (or any video format supported by OpenCV).
    output_dir:
        Directory in which the extracted images are stored.  It is created
        automatically if it does not exist.
    fps:
        Frames to capture per second of video.  Pass 0 (or any non-positive
        value) to capture every frame.

    Returns
    -------
    int
        Number of images written to disk.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video file: {input_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps <= 0:
        video_fps = 25.0  # sensible fallback

    # How many source frames to skip between captures.
    if fps <= 0:
        frame_interval = 1  # capture every frame
    else:
        frame_interval = max(1, round(video_fps / fps))

    basename = os.path.splitext(os.path.basename(input_path))[0]
    saved = 0
    frame_index = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_index % frame_interval == 0:
                filename = os.path.join(output_dir, f"{basename}_frame{frame_index:06d}.jpg")
                if not cv2.imwrite(filename, frame):
                    raise RuntimeError(f"Failed to write image: {filename}")
                saved += 1

            frame_index += 1
    finally:
        cap.release()

    return saved


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract frames from an MP4 file and save them as JPEG images.",
    )
    parser.add_argument("input", help="Path to the input MP4 file.")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help=(
            "Directory to save the extracted images. "
            "Defaults to a sub-folder named after the video in the same directory."
        ),
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=1.0,
        help="Frames per second to capture (default: 1). Use 0 to capture every frame.",
    )
    args = parser.parse_args()

    if args.output_dir is None:
        video_name = os.path.splitext(os.path.basename(args.input))[0]
        args.output_dir = os.path.join(os.path.dirname(os.path.abspath(args.input)), video_name)

    try:
        count = convert(args.input, args.output_dir, args.fps)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Done. {count} image(s) saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
