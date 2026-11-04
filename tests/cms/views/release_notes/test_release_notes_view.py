from __future__ import annotations

import re
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse

from integreat_cms import __version__
from integreat_cms.cms.views.release_notes.release_notes_view import ReleaseNotesView


@pytest.mark.django_db
def test_licenses_link_only_shown_for_current_version(load_test_data: None) -> None:
    """
    Test that the link to the licenses of used software is only shown next to the current version,
    and not next to the most recent version of every year (see issue #4207)

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    """
    client = Client()
    client.force_login(get_user_model().objects.get(username="root"))

    with patch.object(
        ReleaseNotesView, "does_sbom_exist_for_this_version", return_value=True
    ):
        response = client.get(reverse("release_notes"))
    assert response.status_code == 200

    licenses_url = reverse("public:open_source_licenses")
    headings = re.findall(r"<h2.*?</h2>", response.content.decode(), flags=re.DOTALL)
    headings_with_licenses_link = [
        heading for heading in headings if licenses_url in heading
    ]

    assert len(headings_with_licenses_link) == 1
    assert f">{__version__}</a>" in headings_with_licenses_link[0]


@pytest.mark.django_db
def test_licenses_link_not_shown_without_sbom(load_test_data: None) -> None:
    """
    Test that the link to the licenses of used software is not shown if no SBOM exists

    :param load_test_data: The fixture providing the test data (see :meth:`~tests.conftest.load_test_data`)
    """
    client = Client()
    client.force_login(get_user_model().objects.get(username="root"))

    with patch.object(
        ReleaseNotesView, "does_sbom_exist_for_this_version", return_value=False
    ):
        response = client.get(reverse("release_notes"))
    assert response.status_code == 200
    assert reverse("public:open_source_licenses") not in response.content.decode()
