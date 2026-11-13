"""Keep sandbox tests from writing to persistent manual-testing media."""

from tempfile import TemporaryDirectory

from django.test import override_settings
from django.test.runner import DiscoverRunner


class SandboxTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        self.media = TemporaryDirectory(prefix="wagtail-qrcode-sandbox-tests-")
        self.storage_settings = override_settings(MEDIA_ROOT=self.media.name)
        self.storage_settings.enable()

    def teardown_test_environment(self, **kwargs):
        self.storage_settings.disable()
        self.media.cleanup()
        super().teardown_test_environment(**kwargs)
