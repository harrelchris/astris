"""Update Static Data Export

Models use foreign keys, while static data uses integers.
In order to insert using integers, foreign key checks are
disabled and static data fields are labeled as <field>_id.
"""

import sys

from django.core.management.base import BaseCommand
from django.db import transaction

from sde import pipelines
from sde.models import Hash
from sde.services import disable_foreign_key_verification, enable_foreign_key_verification, get_remote_hash

PIPELINES = [
    pipelines.CategoryPipeline(),
    pipelines.GroupPipeline(),
    pipelines.MarketGroupPipeline(),
    pipelines.TypePipeline(),
    pipelines.MetaGroupPipeline(),
    pipelines.MetaTypePipeline(),
]


class Command(BaseCommand):
    help = "Update static data"

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Run even if static data is current",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Checking for updates..."))
        local_hash, created = Hash.objects.get_or_create(id=1, defaults=dict(value=""))
        remote_hash = get_remote_hash()
        if local_hash.is_current(remote_hash=remote_hash) and not options["force"]:
            self.stdout.write(self.style.SUCCESS("Static data is current"))
            sys.exit(0)

        self.stdout.write(self.style.WARNING("Updating static data..."))
        disable_foreign_key_verification()
        with transaction.atomic():
            for pipeline in PIPELINES:
                pipeline.run()
        enable_foreign_key_verification()
        local_hash.update_hash(remote_hash=remote_hash)
        self.stdout.write(self.style.SUCCESS("Static data updated"))
