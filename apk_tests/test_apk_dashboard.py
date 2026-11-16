"""
Dashboard and navigation tests - Food On Demand manager APK.
Logs in once as the outlet manager (buffet / 123) and checks every main screen.

NOTE: the screens behind Create Order, Orders, Chat, Reports and Settings have not been seen yet,
so these tests check that each one opens (the dashboard disappears) and that Back / Home
returns. After the first run, open each screen with dump_screen.py and add exact checks.
"""
import os
import time
import pytest

import ui
from ui import by_id, on_dashboard

USER = os.getenv("APK_USERNAME", "buffet")


# ------------------------------------------------------------ dashboard content

def test_dashboard_greeting_and_user(home):
    assert home.find_element(*by_id("text_view_user_greeting")).text.lower() == USER.lower()
    assert ui.has_text(home, "Good morning") or ui.has_text(home, "Good afternoon") \
        or ui.has_text(home, "Good evening")


def test_dashboard_shows_outlet_name(home):
    assert home.find_element(*by_id("dashboard_title")).text.strip() != ""


def test_dashboard_shows_todays_overview(home):
    assert ui.has_text(home, "TODAY'S OVERVIEW")
    assert home.find_element(*by_id("tv_today_date")).text.strip() != ""


@pytest.mark.parametrize("stat", ["tv_stat_total", "tv_stat_active", "tv_stat_served"])
def test_dashboard_stat_is_a_number(home, stat):
    assert home.find_element(*by_id(stat)).text.strip().isdigit()


def test_total_is_not_less_than_active_plus_served(home):
    total = int(home.find_element(*by_id("tv_stat_total")).text)
    active = int(home.find_element(*by_id("tv_stat_active")).text)
    served = int(home.find_element(*by_id("tv_stat_served")).text)
    assert total >= active + served or total == active + served, f"total={total} active={active} served={served}"


@pytest.mark.parametrize("label", ["Create Order", "View Orders", "Chat", "Report", "Settings", "QUICK ACTIONS"])
def test_quick_actions_present(home, label):
    assert ui.has_text(home, label), f"'{label}' missing on the dashboard"


@pytest.mark.parametrize("tab", ["Home", "Orders", "Chat", "Reports", "Settings"])
def test_bottom_navigation_tabs_present(home, tab):
    assert ui.has_text(home, tab), f"Bottom tab '{tab}' missing"


def test_footer_shows_version_and_device_id(home):
    assert "1.0.1" in home.find_element(*by_id("appVersionTxtID")).text
    assert "Device ID" in home.find_element(*by_id("deviceIdTxt")).text


def test_refresh_stats_keeps_dashboard(home):
    ui.tap_id(home, "btn_refresh_stats")
    time.sleep(3)
    assert on_dashboard(home), "Refresh closed or broke the dashboard"


# ------------------------------------------------------------ bottom navigation

@pytest.mark.parametrize("tab", ["Orders", "Chat", "Reports", "Settings"])
def test_bottom_tab_opens_and_home_returns(home, tab):
    ui.tap_text(home, tab)
    time.sleep(3)
    assert not on_dashboard(home), f"'{tab}' tab did not open a new screen"
    ui.tap_text(home, "Home")
    time.sleep(2.5)
    assert on_dashboard(home), "Home tab did not return to the dashboard"


# ------------------------------------------------------------ quick action cards

@pytest.mark.parametrize("card", ["Create Order", "View Orders", "Report", "Settings"])
def test_quick_action_opens_and_back_returns(home, card):
    ui.tap_text(home, card)
    time.sleep(3)
    assert not on_dashboard(home), f"'{card}' did not open a screen"
    ui.press_back()
    time.sleep(2)
    if not on_dashboard(home):
        ui.tap_text(home, "Home")
        time.sleep(2)
    assert on_dashboard(home), f"Could not get back to the dashboard from '{card}'"


# ------------------------------------------------------------ logout pop-up

def test_logout_popup_content(home):
    ui.logout_icon(home)
    assert ui.wait_for_text(home, "Are you sure you want to logout?", 8), "Logout pop-up did not open"
    assert ui.has_text(home, "Cancel") and ui.has_text(home, "Logout")
    ui.tap_text(home, "Cancel")
    time.sleep(1.5)
    assert on_dashboard(home)


def test_back_button_on_logout_popup_closes_it(home):
    ui.logout_icon(home)
    assert ui.wait_for_text(home, "Are you sure you want to logout?", 8)
    ui.press_back()
    time.sleep(1.5)
    assert not ui.has_text(home, "Are you sure you want to logout?"), "Pop-up still open after Back"
    assert on_dashboard(home)
