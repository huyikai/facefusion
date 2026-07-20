#!/usr/bin/env python3
"""Split a long target video into many trim ranges, run headless-run per segment, then concat.

Example:
  python scripts/segment_headless_run.py \\
    --source /path/to/face.jpg \\
    --target /path/to/video.mp4 \\
    --output /path/to/final.mp4 \\
    --frames-per-segment 300
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def count_frames(video_path: Path) -> int:
	command = [
		'ffprobe', '-v', 'error',
		'-select_streams', 'v:0',
		'-count_packets',
		'-show_entries', 'stream=nb_read_packets',
		'-of', 'csv=p=0',
		str(video_path)
	]
	result = subprocess.run(command, check = True, capture_output = True, text = True)
	value = result.stdout.strip().splitlines()[-1].strip()
	return int(value)


def build_segments(total_frames: int, frames_per_segment: int) -> list[tuple[int, int]]:
	segments: list[tuple[int, int]] = []
	start = 0
	while start < total_frames:
		end = min(start + frames_per_segment, total_frames)
		segments.append((start, end))
		start = end
	return segments


def run(command: list[str], dry_run: bool) -> None:
	print('+', ' '.join(command), flush = True)
	if dry_run:
		return
	subprocess.run(command, check = True)


def main() -> int:
	parser = argparse.ArgumentParser(description = 'Segmented FaceFusion headless-run + ffmpeg concat')
	parser.add_argument('--source', required = True, help = 'Source face image path')
	parser.add_argument('--target', required = True, help = 'Target video path')
	parser.add_argument('--output', required = True, help = 'Final concatenated output path')
	parser.add_argument('--frames-per-segment', type = int, default = 300, help = 'Frames per segment (default: 300)')
	parser.add_argument('--processors', nargs = '+', default = [ 'face_swapper' ])
	parser.add_argument('--execution-providers', nargs = '+', default = [ 'coreml' ])
	parser.add_argument('--workdir', default = '', help = 'Directory for part videos (default: <output>_parts)')
	parser.add_argument('--skip-existing', action = 'store_true', help = 'Skip segments whose part file already exists')
	parser.add_argument('--dry-run', action = 'store_true', help = 'Print commands only')
	parser.add_argument('--python', default = sys.executable, help = 'Python interpreter for facefusion.py')
	args, extra_args = parser.parse_known_args()
	if extra_args and extra_args[0] == '--':
		extra_args = extra_args[1:]

	repo_root = Path(__file__).resolve().parents[1]
	facefusion_py = repo_root / 'facefusion.py'
	source = Path(args.source).expanduser().resolve()
	target = Path(args.target).expanduser().resolve()
	output = Path(args.output).expanduser().resolve()

	if not source.is_file():
		raise SystemExit(f'source not found: {source}')
	if not target.is_file():
		raise SystemExit(f'target not found: {target}')
	if args.frames_per_segment < 30:
		raise SystemExit('--frames-per-segment should be >= 30')

	workdir = Path(args.workdir).expanduser().resolve() if args.workdir else Path(str(output) + '_parts')
	workdir.mkdir(parents = True, exist_ok = True)
	output.parent.mkdir(parents = True, exist_ok = True)

	total_frames = count_frames(target)
	segments = build_segments(total_frames, args.frames_per_segment)
	print(f'target frames: {total_frames}')
	print(f'segments: {len(segments)} x ~{args.frames_per_segment} frames')
	print(f'workdir: {workdir}')

	part_paths: list[Path] = []

	for index, (start, end) in enumerate(segments, start = 1):
		part_path = workdir / f'part_{index:03d}_{start}_{end}{output.suffix or ".mp4"}'
		part_paths.append(part_path)
		if args.skip_existing and part_path.is_file() and part_path.stat().st_size > 0:
			print(f'[skip] {part_path.name} already exists')
			continue

		command = [
			args.python, str(facefusion_py), 'headless-run',
			'--source-paths', str(source),
			'--target-path', str(target),
			'--output-path', str(part_path),
			'--processors', *args.processors,
			'--execution-providers', *args.execution_providers,
			'--trim-frame-start', str(start),
			'--trim-frame-end', str(end),
			*extra_args
		]
		print(f'[segment {index}/{len(segments)}] frames [{start}, {end})')
		run(command, args.dry_run)

	missing = [ path for path in part_paths if not path.is_file() or path.stat().st_size == 0 ]
	if missing and not args.dry_run:
		raise SystemExit('missing part files:\n' + '\n'.join(str(path) for path in missing))

	list_path = workdir / 'concat_list.txt'
	list_body = ''.join(f"file '{part_path.resolve()}'\n" for part_path in part_paths)
	if not args.dry_run:
		list_path.write_text(list_body, encoding = 'utf-8')

	concat_command = [
		'ffmpeg', '-y',
		'-f', 'concat',
		'-safe', '0',
		'-i', str(list_path),
		'-c', 'copy',
		str(output)
	]
	print('[concat] merging parts ->', output)
	run(concat_command, args.dry_run)
	print('done:', output)
	return 0


if __name__ == '__main__':
	raise SystemExit(main())
