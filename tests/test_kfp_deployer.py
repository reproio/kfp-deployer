import kfp_deployer
from datetime import datetime, timezone
from kfp_deployer import main, __version__


def test_version():
    assert __version__ == "0.1.0"


class TestVersionGenerator:
    def test_version_str_default(self):
        base_timestamp = datetime(2020, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
        expected = "test-pipeline-v201231-123456"
        actual = main.create_version_str("test-pipeline", "UTC", base_timestamp)
        assert actual == expected

    def test_version_str_current_time(self):
        expected_prefix = "test-pipeline-v"
        actual = main.create_version_str("test-pipeline", "UTC")
        assert actual[: len(expected_prefix)] == expected_prefix

    def test_version_str_local_time(self):
        base_timestamp = datetime(2020, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
        expected = "test-pipeline-v201231-213456"  # +9
        actual = main.create_version_str("test-pipeline", "JST", base_timestamp)
        assert actual == expected
