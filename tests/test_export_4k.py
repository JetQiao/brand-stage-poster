"""验证文件安全、真实像素尺寸和内容保护，不调用任何图像生成服务。"""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image, ImageCms, PngImagePlugin


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_4k.py"
SPEC = importlib.util.spec_from_file_location("export_4k", SCRIPT)
export_4k = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_4k)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.output = self.root / "output"
        self.source = self.root / "source.png"

    def write_image(self, size=(80, 40), mode="RGB", color="red", **options):
        Image.new(mode, size, color).save(self.source, **options)
        return self.source

    def export(self, **options):
        return export_4k.export_image(self.source, self.output, **options)

    def test_landscape_portrait_and_small_rounding_preserve_proportions(self):
        for size, expected in [((80, 40), (40, 20)), ((40, 80), (20, 40)), ((11, 7), (40, 25))]:
            with self.subTest(size=size):
                self.write_image(size)
                before = self.source.read_bytes()
                report = self.export(long_edge=40, overwrite=True)
                with Image.open(self.output / report["outputs"][0]["file"]) as result:
                    self.assertEqual(result.size, expected)
                    self.assertEqual(result.getpixel((0, 0)), (255, 0, 0))
                self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(report["requested_long_edge"], 40)
        self.assertTrue(report["outputs"][0]["resampled"])

    def test_unchanged_size_preserves_rgba_pixels_and_strips_private_metadata(self):
        exif = Image.Exif()
        exif[315] = "PRIVATE AUTHOR"
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("Description", "PRIVATE TEXT")
        self.write_image((2, 1), "RGBA", (70, 90, 110, 80), exif=exif, pnginfo=pnginfo)
        report = self.export(long_edge=2)
        with Image.open(self.output / "poster_long-edge-2.png") as result:
            self.assertEqual(result.mode, "RGBA")
            self.assertEqual(result.getpixel((0, 0)), (70, 90, 110, 80))
            self.assertFalse(result.getexif())
            self.assertNotIn("Description", result.info)
        self.assertFalse(report["outputs"][0]["resampled"])

    def test_uhd_preserves_full_content_and_composites_transparency_on_black(self):
        image = Image.new("RGBA", (40, 40), (255, 0, 0, 255))
        image.paste((0, 255, 0, 255), (0, 0, 40, 5))
        image.paste((0, 0, 255, 255), (0, 35, 40, 40))
        image.paste((0, 0, 0, 0), (10, 10, 30, 30))
        image.save(self.source)
        report = self.export(long_edge=80, uhd=True)
        with Image.open(self.output / "poster_uhd.png") as result:
            self.assertEqual(result.size, (3840, 2160))
            self.assertEqual(result.mode, "RGB")
            self.assertEqual(result.getpixel((0, 1080)), (0, 0, 0))
            self.assertEqual(result.getpixel((840, 1000)), (255, 0, 0))
            self.assertEqual(result.getpixel((1920, 0)), (0, 255, 0))
            self.assertEqual(result.getpixel((1920, 2159)), (0, 0, 255))
            self.assertEqual(result.getpixel((1920, 1080)), (0, 0, 0))
        self.assertEqual(report["outputs"][1]["padding"], {"left": 840, "top": 0, "right": 840, "bottom": 0})
        self.assertEqual(report["outputs"][1]["content_size"], [2160, 2160])

    def test_exif_orientation_is_applied_before_size_calculation(self):
        exif = Image.Exif()
        exif[274] = 6
        image = Image.new("RGB", (40, 20), "red")
        image.paste("blue", (20, 0, 40, 20))
        image.save(self.source, exif=exif)
        report = self.export(long_edge=40)
        with Image.open(self.output / "poster_long-edge-40.png") as result:
            self.assertEqual(result.size, (20, 40))
            self.assertEqual(result.getpixel((10, 5)), (255, 0, 0))
            self.assertEqual(result.getpixel((10, 35)), (0, 0, 255))
            self.assertFalse(result.getexif())
        self.assertTrue(report["exif_orientation_applied"])
        self.assertFalse(report["outputs"][0]["resampled"])

    def test_valid_rgb_icc_is_preserved_and_invalid_icc_is_reported(self):
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        for icc, status in [(profile, "preserved"), (b"not an ICC profile", "discarded_invalid_or_unsupported")]:
            with self.subTest(status=status):
                self.write_image(icc_profile=icc)
                report = self.export(long_edge=80, overwrite=True)
                with Image.open(self.output / "poster_long-edge-80.png") as result:
                    self.assertEqual(result.info.get("icc_profile"), profile if status == "preserved" else None)
                self.assertEqual(report["metadata"]["icc_profile"], status)

    def test_existing_report_blocks_every_output_before_encoding(self):
        self.write_image()
        self.output.mkdir()
        existing = self.output / "poster_export.json"
        existing.write_text("keep me", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.export(long_edge=80, uhd=True)
        self.assertEqual(list(self.output.iterdir()), [existing])
        self.assertEqual(existing.read_text(encoding="utf-8"), "keep me")

    def test_never_overwrites_input_or_its_links_even_with_overwrite(self):
        self.write_image()
        before = self.source.read_bytes()
        self.output.mkdir()
        for kind, filename in [("symlink", "poster_long-edge-80.png"), ("hardlink", "poster_export.json")]:
            with self.subTest(kind=kind):
                target = self.output / filename
                if kind == "symlink":
                    target.symlink_to(self.source)
                else:
                    os.link(self.source, target)
                with self.assertRaises(ValueError):
                    self.export(long_edge=80, overwrite=True)
                self.assertEqual(self.source.read_bytes(), before)
                target.unlink()
        for filename in ["poster_long-edge-80.png", "poster_export.json"]:
            target = self.output / filename
            target.write_bytes(before)
            with self.assertRaises(ValueError):
                export_4k.export_image(target, self.output, long_edge=80, overwrite=True)
            self.assertEqual(target.read_bytes(), before)
            target.unlink()

    def test_encoding_failure_does_not_leave_outputs_or_replace_existing_files(self):
        self.write_image()
        self.export(long_edge=80)
        before = {path.name: path.read_bytes() for path in self.output.iterdir()}
        real_save = Image.Image.save

        def fail_on_uhd(image, file, *args, **kwargs):
            if Path(file).name == "poster_uhd.png":
                raise OSError("simulated encoding failure")
            return real_save(image, file, *args, **kwargs)

        with mock.patch.object(Image.Image, "save", fail_on_uhd):
            with self.assertRaisesRegex(OSError, "encoding"):
                self.export(long_edge=80, uhd=True, overwrite=True)
        self.assertEqual({path.name: path.read_bytes() for path in self.output.iterdir()}, before)

    def test_commit_failure_rolls_back_existing_outputs(self):
        self.write_image()
        self.export(long_edge=80)
        before = {path.name: path.read_bytes() for path in self.output.iterdir()}
        real_link = os.link

        def fail_on_report(source, target):
            if Path(target).suffix == ".json":
                raise OSError("simulated commit failure")
            return real_link(source, target)

        with mock.patch.object(export_4k.os, "link", fail_on_report):
            with self.assertRaisesRegex(OSError, "commit"):
                self.export(long_edge=80, overwrite=True)
        self.assertEqual({path.name: path.read_bytes() for path in self.output.iterdir()}, before)

    def test_cli_report_has_real_dimensions_and_no_absolute_paths(self):
        self.write_image((4, 8))
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(self.source), "--output-dir", str(self.output)],
            capture_output=True, text=True, check=True,
        )
        report = json.loads(result.stdout)
        saved = json.loads((self.output / "poster_export.json").read_text(encoding="utf-8"))
        self.assertEqual(report, saved)
        self.assertEqual(report["outputs"][0]["size"], [2048, 4096])
        self.assertFalse(report["ai_super_resolution"])
        self.assertFalse(report["generated_new_detail"])
        self.assertNotIn(str(self.root), result.stdout)
        with Image.open(self.output / report["outputs"][0]["file"]) as result_image:
            self.assertEqual(list(result_image.size), report["outputs"][0]["size"])

    def test_cli_invalid_arguments_and_invalid_input_fail_without_outputs(self):
        self.source.write_text("not an image", encoding="utf-8")
        base = [sys.executable, str(SCRIPT), "--input", str(self.source), "--output-dir", str(self.output)]
        for extra in [[], ["--long-edge", "0"], ["--prefix", "../outside"]]:
            with self.subTest(extra=extra):
                result = subprocess.run(base + extra, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
