"""
LV-054 Admin Step (Standalone): Configure Min/Max Days in Leave Master

  - Login as HR Admin (SSSRC018)
  - Navigate to Master Settings → Masters → Attendance → Leave Type
  - Open "Additional Details" for the leave type
  - Set "Min No. of Days" and "Max No.of Days"
  - Click Update → Logout

URL:  https://qa-current.247hrmstaging.com:8452
"""

import os
import sys
import io
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ========== CONFIGURATION ==========
URL = "https://qa-current.247hrmstaging.com:8452"
ADMIN_ID = "SSSRC018"
ADMIN_PASS = "sys"

MIN_DAYS_SETTING = "1"      # Admin sets min days to this value
MAX_DAYS_SETTING = "3"      # Admin sets max days to this value

SCREENSHOT_DIR = os.path.dirname(os.path.abspath(__file__))
# ====================================

test_verdict = "INCONCLUSIVE"


def take_screenshot(page, name):
    """Save a screenshot with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
    page.screenshot(path=filepath)
    print(f"[SCREENSHOT] Saved: {filepath}")
    return filepath


def capture_system_message(page):
    """Check for toast/snackbar/alert messages."""
    selectors = [
        "simple-snack-bar",
        ".mat-snack-bar-container",
        ".cdk-overlay-container .mat-snack-bar-container",
        "snack-bar-container",
        ".toast-message",
        "alertdialog",
        "mat-dialog-container",
    ]
    for selector in selectors:
        try:
            el = page.locator(selector).first
            if el.is_visible(timeout=2000):
                msg = el.inner_text().strip()
                if msg:
                    print(f"[INFO] System message found ({selector}): {msg}")
                    return msg
        except Exception:
            continue
    return None


def admin_configure_min_max(page):
    """
    Admin login → Masters → Attendance → Leave Type → Additional Details
    Set Min No. of Days and Max No.of Days → Update → Logout
    """

    # --- LOGIN ---
    print("\n" + "=" * 60)
    print(f"[ADMIN STEP 1] Logging in as HR Admin ({ADMIN_ID})...")
    print("=" * 60)

    page.goto(f"{URL}/#/login")
    page.get_by_role("textbox", name="Employee Id").wait_for(state="visible", timeout=15000)
    page.get_by_role("textbox", name="Employee Id").click()
    page.get_by_role("textbox", name="Employee Id").fill(ADMIN_ID)
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(ADMIN_PASS)
    page.get_by_role("button", name="LOG IN").click()

    page.wait_for_url("**/dashboard/welcomePage*", timeout=60000)
    page.wait_for_timeout(3000)
    print("[ADMIN STEP 1] [PASS] Admin login successful!")
    take_screenshot(page, "masters_login_success")

    # --- NAVIGATE TO LEAVE TYPE MASTER ---
    print("[ADMIN STEP 2] Navigating: Settings → Masters → Attendance → Leave Type...")

    page.locator("button").filter(has_text="settings").click()
    page.wait_for_timeout(2000)

    page.get_by_role("menuitem", name="Masters").click()
    page.wait_for_timeout(3000)
    take_screenshot(page, "masters_page")

    page.get_by_text("Attendancechevron_right").click()
    page.wait_for_timeout(2000)

    page.get_by_role("button", name="Leave Type Configure leave").click()
    page.wait_for_timeout(3000)
    take_screenshot(page, "masters_leave_type_list")

    # --- EXPAND ROW & SET MIN/MAX DAYS ---
    print("[ADMIN STEP 3] Expanding leave type row and setting Min/Max Days...")

    page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(2).click()
    page.wait_for_timeout(2000)
    take_screenshot(page, "masters_row_expanded")

    page.get_by_text("Additional Details").click()
    page.wait_for_timeout(2000)
    take_screenshot(page, "masters_additional_details")

    # Set Min No. of Days
    min_days_field = page.get_by_role("textbox", name="Min No. of Days")
    min_days_field.wait_for(state="visible", timeout=10000)
    min_days_field.click()
    min_days_field.fill(MIN_DAYS_SETTING)
    min_days_field.press("Enter")
    page.wait_for_timeout(1000)
    print(f"[ADMIN STEP 3] Min No. of Days set to {MIN_DAYS_SETTING}")

    # Set Max No.of Days
    max_days_field = page.get_by_role("textbox", name="Max No.of Days")
    max_days_field.click()
    max_days_field.fill(MAX_DAYS_SETTING)
    max_days_field.press("Enter")
    page.wait_for_timeout(1000)
    print(f"[ADMIN STEP 3] Max No.of Days set to {MAX_DAYS_SETTING}")
    take_screenshot(page, "masters_min_max_set")

    # Click Update
    page.get_by_role("button", name="Update").click()
    page.wait_for_timeout(3000)

    msg = capture_system_message(page)
    if msg:
        print(f"[ADMIN STEP 3] System response: {msg}")
    take_screenshot(page, "masters_updated")
    print(f"[ADMIN STEP 3] [PASS] Min={MIN_DAYS_SETTING}, Max={MAX_DAYS_SETTING} updated!")

    # --- LOGOUT ---
    print("[ADMIN STEP 4] Logging out admin...")

    profile_btn = page.get_by_role("button", name=re.compile(r".*SSSRC018.*"))
    profile_btn.click()
    page.wait_for_timeout(1500)

    page.get_by_role("menuitem", name="Logout").click()
    page.wait_for_timeout(3000)
    take_screenshot(page, "masters_logged_out")
    print("[ADMIN STEP 4] [PASS] Admin logged out!")


# =====================================================================
#  MAIN EXECUTION
# =====================================================================

def run_masters_config():
    """Run the Admin master settings configuration."""
    global test_verdict

    print("=" * 70)
    print("  LV-054 Admin: Configure Min/Max Days in Leave Master")
    print(f"  Min={MIN_DAYS_SETTING}, Max={MAX_DAYS_SETTING}")
    print("=" * 70)
    print(f"  Admin: {ADMIN_ID}")
    print("=" * 70)
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        try:
            admin_configure_min_max(page)
            test_verdict = "PASS"

        except Exception as e:
            print(f"\n[FATAL ERROR] {str(e)}")
            test_verdict = "FAIL"
            try:
                take_screenshot(page, "fatal_error")
            except Exception:
                pass

        finally:
            print("\n" + "=" * 70)
            print(f"  FINAL VERDICT: {test_verdict}")
            if test_verdict == "PASS":
                print(f"  Admin successfully set Min={MIN_DAYS_SETTING}, Max={MAX_DAYS_SETTING}")
            else:
                print("  Admin configuration failed — check screenshots")
            print(f"  Screenshots saved to: {SCREENSHOT_DIR}")
            print("=" * 70)

            try:
                take_screenshot(page, f"VERDICT_{test_verdict}")
            except Exception:
                pass

            browser.close()


if __name__ == "__main__":
    run_masters_config()
