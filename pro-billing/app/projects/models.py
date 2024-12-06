import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from models import TimestampModel, UUIDModel
from forgestripe.models import StripeModel

from github import invite_username_to_repo, remove_username_from_repo
from packages.models import Package


class Project(TimestampModel, UUIDModel, StripeModel):
    name = models.SlugField(
        unique=True, max_length=255, help_text="Unique slug across all projects"
    )
    team = models.ForeignKey(
        "teams.Team", on_delete=models.CASCADE, related_name="projects"
    )
    # url?

    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    terms_accepted_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    packages_token = models.UUIDField(default=uuid.uuid4)

    # Person (people) who will be invited to repo for this project
    github_usernames = ArrayField(
        models.SlugField(max_length=255), blank=True, null=True
    )

    # Mostly used for the Stripe status
    status = models.CharField(max_length=255, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return self.status == "active"

    def sync_stripe(self):
        subscription = self.get_stripe_object()
        if subscription:
            self.status = subscription.status
        else:
            self.status = ""
        self.save()

    def invite_github_usernames(self):
        for package in Package.objects.all():
            for username in self.github_usernames:
                invite_username_to_repo(username, package.repo_full_name)

    def remove_github_usernames(self):
        for package in Package.objects.all():
            for username in self.github_usernames:
                has_other_projects = (
                    Project.objects.exclude(id=self.id)
                    .filter(status="active", github_usernames__icontains=username)
                    .exists()
                )
                if not has_other_projects:
                    remove_username_from_repo(username, package.repo_full_name)
