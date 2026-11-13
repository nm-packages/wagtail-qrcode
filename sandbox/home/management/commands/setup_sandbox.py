"""Create missing examples without replacing contributor edits."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from home.models import HomePage, QRCodePage
from wagtail.coreutils import find_available_slug
from wagtail.models import Site


class Command(BaseCommand):
    help = "Migrate and create missing sandbox examples and a local admin/admin user."

    def handle(self, *args, **options):
        call_command("migrate", interactive=False, verbosity=options["verbosity"])
        self.seed()
        self.stdout.write(
            self.style.SUCCESS(f"Sandbox ready: {settings.SANDBOX_BASE_URL}")
        )
        self.stdout.write(
            "Local login: admin / admin (existing passwords are preserved)."
        )

    @transaction.atomic
    def seed(self):
        users = get_user_model().objects
        if not users.filter(username="admin").exists():
            users.create_superuser("admin", "admin@example.test", "admin")

        home = HomePage.objects.order_by("pk").first()
        # The supplied scaffold migration creates this homepage and its Site.
        if home is None:
            from wagtail.models import Page

            home = Page.get_first_root_node().add_child(
                instance=HomePage(title="Sandbox home", slug="home")
            )
            home.save_revision().publish()
        site = Site.objects.filter(root_page=home).order_by("pk").first()
        if site is None:
            site = Site(root_page=home, is_default_site=not Site.objects.exists())
        site.hostname = settings.SANDBOX_HOST
        site.port = settings.SANDBOX_PORT
        site.site_name = "Wagtail QR code sandbox"
        site.save()

        for key, title, live in [
            ("published", "Published QR example — scan and download", True),
            ("draft", "Draft QR example — save and preview", False),
        ]:
            if QRCodePage.objects.filter(sandbox_example=key).exists():
                continue
            page = home.add_child(
                instance=QRCodePage(
                    title=title,
                    slug=find_available_slug(home, f"{key}-qr-example"),
                    live=False,
                    sandbox_example=key,
                )
            )
            revision = page.save_revision()
            if live:
                revision.publish()
