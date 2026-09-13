import os
import unittest
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast
from unittest.mock import patch

import gpt_image

select_deployment = cast(Callable[[], str], getattr(gpt_image, "_select_deployment"))
build_client = cast(Callable[[], tuple[object, str]], getattr(gpt_image, "_build_client"))
select_image_size = cast(Callable[[], str], getattr(gpt_image, "_select_image_size"))
validate_custom_size = cast(
    Callable[[str], str], getattr(gpt_image, "_validate_custom_size")
)


class DeploymentSelectionTests(unittest.TestCase):
    def test_build_client_loads_dotenv_from_current_directory(self) -> None:
        with TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text(
                "AZURE_OPENAI_ENDPOINT=https://example.openai.azure.com\n"
                "OPENAI_API_VERSION=preview\n"
                "AZURE_OPENAI_API_KEY=test-key\n",
                encoding="utf-8",
            )

            with (
                patch.dict(os.environ, {}, clear=True),
                patch("gpt_image.Path.cwd", return_value=Path(temp_dir)),
                patch("gpt_image.prompt", return_value=""),
                patch("gpt_image.AzureOpenAI") as azure_openai,
            ):
                client, deployment = build_client()

        self.assertIs(client, azure_openai.return_value)
        self.assertEqual(deployment, "gpt-image-2.5-flare")
        azure_openai.assert_called_once_with(
            api_version="preview",
            azure_endpoint="https://example.openai.azure.com",
            api_key="test-key",
        )

    def test_selects_numbered_deployment(self) -> None:
        with (
            patch("gpt_image.prompt", return_value="2"),
            patch("builtins.print"),
        ):
            deployment = select_deployment()

        self.assertEqual(deployment, "gpt-image-2.5-sunburst")

    def test_defaults_to_flare(self) -> None:
        with (
            patch("gpt_image.prompt", return_value=""),
            patch("builtins.print"),
        ):
            deployment = select_deployment()

        self.assertEqual(deployment, "gpt-image-2.5-flare")

    def test_rejects_out_of_range_deployment_number(self) -> None:
        with (
            patch("gpt_image.prompt", return_value="3"),
            patch("builtins.print"),
            self.assertRaisesRegex(SystemExit, "1~2"),
        ):
            select_deployment()


class ImageSizeSelectionTests(unittest.TestCase):
    def test_selects_4k_landscape_preset(self) -> None:
        with (
            patch("gpt_image.prompt", return_value="8"),
            patch("builtins.print"),
        ):
            image_size = select_image_size()

        self.assertEqual(image_size, "3840x2160")

    def test_accepts_valid_custom_size(self) -> None:
        with (
            patch("gpt_image.prompt", side_effect=["10", "2048X2048"]),
            patch("builtins.print"),
        ):
            image_size = select_image_size()

        self.assertEqual(image_size, "2048x2048")

    def test_rejects_sizes_outside_model_constraints(self) -> None:
        invalid_sizes = (
            "2047x2048",
            "4096x2048",
            "3200x800",
            "512x512",
            "3840x3840",
        )

        for image_size in invalid_sizes:
            with self.subTest(image_size=image_size), self.assertRaises(SystemExit):
                validate_custom_size(image_size)


if __name__ == "__main__":
    unittest.main()