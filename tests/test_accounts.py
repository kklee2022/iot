"""Tests for approval-gated login flow."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestLoginPage:
    def test_login_page_renders(self, client):
        response = client.get(reverse("accounts:login"))
        assert response.status_code == 200
        assert b"Sign in to IoT Platform" in response.content


@pytest.mark.django_db
class TestApprovalGating:
    def test_active_user_can_log_in(self, client, django_user_model):
        django_user_model.objects.create_user(username="alice", password="secret-pass-1", is_active=True)
        response = client.post(
            reverse("accounts:login"),
            data={"username": "alice", "password": "secret-pass-1"},
        )
        assert response.status_code == 302

    def test_inactive_user_sees_pending_message(self, client, django_user_model):
        django_user_model.objects.create_user(username="bob", password="secret-pass-2", is_active=False)
        response = client.post(
            reverse("accounts:login"),
            data={"username": "bob", "password": "secret-pass-2"},
        )
        assert response.status_code == 200
        assert b"pending administrator approval" in response.content

    def test_wrong_password_shows_invalid_login(self, client, django_user_model):
        django_user_model.objects.create_user(username="carol", password="secret-pass-3", is_active=True)
        response = client.post(
            reverse("accounts:login"),
            data={"username": "carol", "password": "wrong"},
        )
        assert response.status_code == 200
        assert b"Incorrect username or password" in response.content


@pytest.mark.django_db
class TestUIAuthGate:
    def test_anonymous_redirected_from_index(self, client):
        response = client.get(reverse("ui-index"))
        assert response.status_code == 302
        assert reverse("accounts:login") in response["Location"]

    def test_authenticated_user_reaches_index(self, client, django_user_model):
        django_user_model.objects.create_user(username="dora", password="secret-pass-4", is_active=True)
        client.login(username="dora", password="secret-pass-4")
        response = client.get(reverse("ui-index"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestLogout:
    def test_logout_redirects_to_login(self, client, django_user_model):
        django_user_model.objects.create_user(username="erin", password="secret-pass-5", is_active=True)
        client.login(username="erin", password="secret-pass-5")
        response = client.post(reverse("accounts:logout"))
        assert response.status_code == 302
