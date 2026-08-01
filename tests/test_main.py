import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/script")))

import main


class TestMain(unittest.TestCase):
    def _run_main(self, apps, member_only=None, argv=None, setapp_search_mode=None):
        env = {}
        if member_only is not None:
            env["member_only"] = member_only
        if setapp_search_mode is not None:
            env["setapp_search_mode"] = setapp_search_mode

        args = argv if argv is not None else ["main.py"]

        with patch("main.load_apps", return_value=apps), \
             patch("main.download_icon", return_value=""), \
             patch("main.alfred_cache_dir", return_value="/tmp"), \
             patch.object(sys, "argv", args), \
             patch.dict(os.environ, env, clear=False):
            out = io.StringIO()
            with redirect_stdout(out):
                main.main()
            return json.loads(out.getvalue())

    def test_member_only_enabled_filters_standalone(self):
        apps = [
            {"uid": 1, "title": "Member App", "subtitle": "", "arg": "https://example.com/a", "membership": True},
            {"uid": 2, "title": "Standalone App", "subtitle": "", "arg": "https://example.com/b", "membership": False},
        ]

        result = self._run_main(apps, member_only="1")
        titles = [item["title"] for item in result["items"]]

        self.assertEqual(titles, ["Member App"])

    def test_member_only_disabled_shows_all(self):
        apps = [
            {"uid": 1, "title": "Member App", "subtitle": "", "arg": "https://example.com/a", "membership": True},
            {"uid": 2, "title": "Standalone App", "subtitle": "", "arg": "https://example.com/b", "membership": False},
        ]

        result = self._run_main(apps, member_only="0")
        titles = [item["title"] for item in result["items"]]

        self.assertEqual(titles, ["Member App", "Standalone App"])

    def test_env_var_enabled_truthy_values(self):
        with patch.dict(os.environ, {"member_only": "true"}, clear=False):
            self.assertTrue(main.env_var_enabled("member_only"))
        with patch.dict(os.environ, {"member_only": "on"}, clear=False):
            self.assertTrue(main.env_var_enabled("member_only"))
        with patch.dict(os.environ, {"member_only": "0"}, clear=False):
            self.assertFalse(main.env_var_enabled("member_only"))

    def test_standalone_mode_argument_shows_only_standalone(self):
        apps = [
            {"uid": 1, "title": "Member App", "subtitle": "", "arg": "https://example.com/a", "membership": True},
            {"uid": 2, "title": "Standalone App", "subtitle": "", "arg": "https://example.com/b", "membership": False},
        ]

        result = self._run_main(apps, argv=["main.py", "", "standalone"])
        titles = [item["title"] for item in result["items"]]

        self.assertEqual(titles, ["Standalone App"])

    def test_standalone_mode_env_shows_only_standalone(self):
        apps = [
            {"uid": 1, "title": "Member App", "subtitle": "", "arg": "https://example.com/a", "membership": True},
            {"uid": 2, "title": "Standalone App", "subtitle": "", "arg": "https://example.com/b", "membership": False},
        ]

        result = self._run_main(apps, setapp_search_mode="setas")
        titles = [item["title"] for item in result["items"]]

        self.assertEqual(titles, ["Standalone App"])

    def test_membership_mode_argument_setam_shows_only_membership(self):
        apps = [
            {"uid": 1, "title": "Member App", "subtitle": "", "arg": "https://example.com/a", "membership": True},
            {"uid": 2, "title": "Standalone App", "subtitle": "", "arg": "https://example.com/b", "membership": False},
        ]

        result = self._run_main(apps, argv=["main.py", "", "setam"])
        titles = [item["title"] for item in result["items"]]

        self.assertEqual(titles, ["Member App"])


if __name__ == "__main__":
    unittest.main()
