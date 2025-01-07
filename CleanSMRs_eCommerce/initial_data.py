from django.contrib.auth.models import Group


def create_groups(apps, schema_editor):
    """Creates some initial groups for the website."""

    groups = ["Site User", "Site Admin"]
    for group_name in groups:
        Group.objects.create(name=group_name)
