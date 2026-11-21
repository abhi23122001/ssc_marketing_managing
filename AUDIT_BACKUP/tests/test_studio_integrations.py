import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from foundation.store import Store
from foundation.domains import ai_image_gen
from foundation.domains import ai_video_gen
from foundation.domains import social_integrations
from foundation.domains import google_sheets_sync


class TestStudioIntegrations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sgcc_foundation.sqlite"))
        cls.store = Store(db_path)

    def test_01_ai_image_prompt_enhancement(self):
        p = "DGPS Land Survey at Jayant Coal"
        enh = ai_image_gen.enhance_prompt(p, "surveying_dgps", "SSC")
        self.assertIn("DGPS Land Survey", enh)
        self.assertIn("GNSS", enh)
        self.assertIn("Shah Surveyors", enh)

    def test_02_ai_image_generation_and_fallback(self):
        res = ai_image_gen.generate_ai_image(
            self.store,
            "RTK Base Station Observation",
            workspace_id="SSC",
            aspect_ratio="1:1",
            style_key="surveying_dgps",
            save_to_library=True
        )
        self.assertTrue(res["ok"])
        self.assertTrue(os.path.exists(res["output_path"]))
        self.assertTrue(os.path.getsize(res["output_path"]) > 0)
        self.assertIsNotNone(res["asset_id"])
        self.assertIn(res["provider"], ["pollinations_free", "local_vector_canvas"])

    def test_03_ai_video_scene_decomposition(self):
        scenes = ai_video_gen.decompose_script_to_scenes("Highway DGPS Alignment", "", "SSC")
        self.assertEqual(len(scenes), 4)
        self.assertEqual(scenes[0]["scene_number"], 1)
        self.assertTrue("headline" in scenes[0])
        self.assertTrue("subtitle" in scenes[0])

    def test_04_ai_video_ffmpeg_render(self):
        scenes = [
            {"scene_number": 1, "duration": 2.0, "headline": "RTK Precision", "subtitle": "Survey of India Ties"},
            {"scene_number": 2, "duration": 2.0, "headline": "Delivery in 24h", "subtitle": "CAD and GIS Deliverables"}
        ]
        res = ai_video_gen.render_script_video(self.store, "Test DGPS Reel", scenes, "SSC")
        self.assertTrue(res["ok"])
        self.assertTrue(os.path.exists(res["output_path"]))
        self.assertEqual(res["aspect_ratio"], "9:16")
        self.assertEqual(res["duration_seconds"], 4.0)

    def test_05_social_accounts_center(self):
        accs = social_integrations.list_social_accounts(self.store, "SSC")
        self.assertTrue(len(accs) >= 4)
        platforms = {a["platform"] for a in accs}
        self.assertTrue({"instagram", "facebook", "youtube", "linkedin"}.issubset(platforms))

        aid = accs[0]["id"]
        # Test toggle disconnect
        d = social_integrations.toggle_account_connection(self.store, aid, connect=False)
        self.assertEqual(d["connection_status"], "disconnected")
        # Test toggle reconnect
        c = social_integrations.toggle_account_connection(self.store, aid, connect=True)
        self.assertEqual(c["connection_status"], "connected")

        # Test sync
        s = social_integrations.sync_account_telemetry(self.store, aid)
        self.assertTrue(s["ok"])

    def test_06_google_sheets_two_way_sync(self):
        status = google_sheets_sync.get_google_sheets_status(self.store, "SSC")
        self.assertTrue(status["ok"])
        self.assertEqual(status["total_entities_mapped"], 12)

        sync_res = google_sheets_sync.execute_sheets_sync(self.store, "SSC", "all", "bidirectional")
        self.assertTrue(sync_res["ok"])
        self.assertEqual(sync_res["synced_entities_count"], 12)
        self.assertTrue(sync_res["total_records_pushed"] > 0)


if __name__ == "__main__":
    unittest.main()
