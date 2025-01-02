# Future
from __future__ import division, print_function, unicode_literals

# Standard Library
from builtins import str


def test_organization(client):
    user = client.users.get(client.user_id)
    organization = client.organizations.get(user.organization)
    assert str(organization) == organization.name
