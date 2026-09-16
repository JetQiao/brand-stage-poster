#!/usr/bin/env python3
"""保留画面内容的 PNG 尺寸导出；使用 Pillow 重采样，不执行 AI 超分。"""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import re
import tempfile

from PIL import Image, ImageCms, ImageOps


def _check_targets(source: Path, targets: list[Path], overwrite: bool) -> None:
    for index, target in enumerate(targets):
        # 同路径、符号链接和硬链接都不能成为覆盖输入的旁路。
        if target.resolve() == source or (target.exists() and target.samefile(source)):
            raise ValueError(f"输出不能覆盖输入文件：{target.name}")
        if target.is_symlink():
            raise ValueError(f"输出目标不能是符号链接：{target.name}")
        if target.exists():
            if not target.is_file():
                raise ValueError(f"输出目标不是普通文件：{target.name}")
            if not overwrite:
                raise FileExistsError(f"文件已存在，请更换前缀或使用 --overwrite：{target.name}")
        for previous in targets[:index]:
            if target.resolve() == previous.resolve() or (
                target.exists() and previous.exists() and target.samefile(previous)
            ):
                raise ValueError("输出文件之间存在路径或硬链接冲突")


def _prepare_image(image: Image.Image) -> tuple[Image.Image, bytes | None, str]:
    has_alpha = "A" in image.getbands() or "transparency" in image.info
    pixels = image.convert("RGBA" if has_alpha else "RGB")
    profile_bytes = image.info.get("icc_profile")
    profile_status = "absent"
    if profile_bytes:
        try:
            profile = ImageCms.ImageCmsProfile(io.BytesIO(profile_bytes))
            if profile.profile.xcolor_space.strip() == "RGB" and image.mode in (
                "RGB", "RGBA", "P", "PA"
            ):
                profile_status = "preserved"
            else:
                # 颜色模式改变时转换到 sRGB，避免给 RGB 像素误挂 CMYK/灰度配置。
                srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
                color_source = image.convert("L") if image.mode == "LA" else image
                converted = ImageCms.profileToProfile(
                    color_source, profile, srgb, outputMode="RGB"
                )
                if has_alpha:
                    converted.putalpha(pixels.getchannel("A"))
                pixels = converted
                profile_bytes = srgb.tobytes()
                profile_status = "converted_to_srgb"
        except (OSError, TypeError, ValueError, ImageCms.PyCMSError):
            profile_bytes = None
            profile_status = "discarded_invalid_or_unsupported"
    # 仅显式写回通过处理的 ICC；不继承 EXIF、XMP、文本或其他隐私元数据。
    pixels.info.clear()
    return pixels, profile_bytes, profile_status


def _resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return image.copy() if image.size == size else image.resize(size, Image.Resampling.LANCZOS)


def _publish(staging: Path, targets: list[Path], source: Path, overwrite: bool) -> None:
    _check_targets(source, targets, overwrite)
    backups: dict[Path, Path] = {}
    published: list[Path] = []
    try:
        for index, target in enumerate(targets):
            if overwrite and target.exists():
                backup = staging / f"backup-{index}"
                os.replace(target, backup)
                backups[target] = backup
            # 同一文件系统内排他创建，避免默认模式在检查后意外覆盖新出现的文件。
            os.link(staging / target.name, target)
            published.append(target)
    except OSError:
        # 所有编码均已完成；提交阶段的常规 I/O 失败仍回滚到导出前状态。
        for target in reversed(published):
            target.unlink()
        for target, backup in backups.items():
            os.replace(backup, target)
        raise


def export_image(
    input_path: str | Path,
    output_dir: str | Path,
    prefix: str = "poster",
    long_edge: int = 4096,
    uhd: bool = False,
    overwrite: bool = False,
) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", prefix):
        raise ValueError("prefix 仅支持 1–80 位英文字母、数字、下划线或短横线，首位须为字母或数字")
    if not isinstance(long_edge, int) or isinstance(long_edge, bool) or long_edge < 1:
        raise ValueError("long-edge 必须是正整数")
    input_path = Path(input_path)
    source = input_path.resolve(strict=True)
    output_dir = Path(output_dir).resolve()
    main_target = output_dir / f"{prefix}_long-edge-{long_edge}.png"
    uhd_target = output_dir / f"{prefix}_uhd.png"
    report_target = output_dir / f"{prefix}_export.json"
    targets = [main_target] + ([uhd_target] if uhd else []) + [report_target]
    _check_targets(source, targets, overwrite)

    with Image.open(source) as original:
        if getattr(original, "n_frames", 1) != 1:
            raise ValueError("仅支持单帧图片，请先将动图或多页文件导出为静态图片")
        original.load()
        stored_size = original.size
        orientation = original.getexif().get(274, 1)
        upright = ImageOps.exif_transpose(original)
        image, icc_profile, profile_status = _prepare_image(upright)

    width, height = image.size
    scale = long_edge / max(width, height)
    main_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    outputs = [{
        "file": main_target.name,
        "size": list(main_size),
        "content_size": list(main_size),
        "resampled": main_size != image.size,
        "padding": {"left": 0, "top": 0, "right": 0, "bottom": 0},
        "has_padding": False,
        "mode": image.mode,
    }]
    report = {
        "input_file": input_path.name,
        "stored_size": list(stored_size),
        "oriented_size": list(image.size),
        "exif_orientation_applied": orientation in range(2, 9),
        "requested_long_edge": long_edge,
        "method": "Pillow Lanczos resampling when dimensions change",
        "ai_super_resolution": False,
        "generated_new_detail": False,
        "metadata": {"exif_removed": True, "icc_profile": profile_status},
        "outputs": outputs,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    # 所有 PNG 和报告先暂存；编码失败时不会留下部分成品，也不会改动旧输出。
    with tempfile.TemporaryDirectory(prefix=".poster-export-", dir=output_dir) as temporary:
        staging = Path(temporary)
        main_image = _resize(image, main_size)
        main_image.save(staging / main_target.name, format="PNG", icc_profile=icc_profile)
        if uhd:
            fit_scale = min(3840 / width, 2160 / height)
            content_size = (
                max(1, min(3840, round(width * fit_scale))),
                max(1, min(2160, round(height * fit_scale))),
            )
            content = _resize(image, content_size)
            left = (3840 - content.width) // 2
            top = (2160 - content.height) // 2
            canvas = Image.new("RGB", (3840, 2160), (0, 0, 0))
            # 透明内容在 UHD 黑底上合成；常规长边版本继续保留 alpha。
            canvas.paste(content, (left, top), content.getchannel("A") if "A" in content.getbands() else None)
            canvas.save(staging / uhd_target.name, format="PNG", icc_profile=icc_profile)
            padding = {
                "left": left, "top": top,
                "right": 3840 - left - content.width,
                "bottom": 2160 - top - content.height,
            }
            outputs.append({
                "file": uhd_target.name,
                "size": [3840, 2160],
                "content_size": list(content_size),
                "resampled": content_size != image.size,
                "padding": padding,
                "has_padding": any(padding.values()),
                "mode": "RGB",
                "background": "#000000",
            })
        (staging / report_target.name).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _publish(staging, targets, source, overwrite)
    return report


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("必须是正整数") from error
    if number < 1:
        raise argparse.ArgumentTypeError("必须是正整数")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="输入静态图片")
    parser.add_argument("--output-dir", required=True, help="输出文件夹")
    parser.add_argument("--prefix", default="poster", help="安全文件名前缀，默认 poster")
    parser.add_argument("--long-edge", type=_positive_int, default=4096, help="目标长边，默认 4096")
    parser.add_argument("--uhd", action="store_true", help="额外导出 3840×2160 等比例黑边版")
    parser.add_argument("--overwrite", action="store_true", help="允许替换已有输出，始终保护输入")
    arguments = parser.parse_args(argv)
    try:
        report = export_image(
            arguments.input, arguments.output_dir, arguments.prefix,
            arguments.long_edge, arguments.uhd, arguments.overwrite,
        )
    except (OSError, ValueError, Image.DecompressionBombError) as error:
        parser.exit(1, f"导出失败：{error}\n")
    # 控制台使用 ASCII 转义，避免 Windows 管道遇到中文文件名时编码失败。
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
