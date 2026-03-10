"""
Masters: Max Leave Days Configuration — Set Max No.of Days in Leave Master

Scenario (Admin - SSSRC018):
    - Login as HR Admin
    - Navigate to Master Settings → Masters → Attendance → Leave Type
    - Open "Additional Details" for the leave type
    - Set "Max No.of Days" to 2
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

MAX_DAYS_SETTING = "2"      # Admin sets max days to this value

SCREENSHOT_DIR = os.path.dirname(os.path.abspath(__file__))
# ====================================


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


# =====================================================================
#  ADMIN: Set Max No.of Days = 2 in Leave Master
#  (Follows Playwright codegen recording EXACTLY)
# =====================================================================

def admin_step1_login_and_configure(page):
    """
    Exact codegen replay:
      1. goto login
      2. click & fill Employee Id = SSSRC018
      3. click & fill Password = sys, press Enter
      4. click LOG IN
      5. click settings button
      6. click Masters menuitem
      7. click 'Attendancechevron_right' text
      8. click 'Leave Type Configure leave' button
      9. expand row (button filter empty text, nth(2))
     10. click 'Additional Details' text
     11. click & fill Max No.of Days = 2, press Enter
     12. click Update
     13. click profile button (Monisha K [SSSRC018] ...)
     14. click Logout menuitem
    """

    # --- LOGIN (exact codegen) ---
    print("\n" + "=" * 60)
    print("[ADMIN STEP 1] Logging in as HR Admin (SSSRC018)...")
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
    take_screenshot(page, "admin_step1_login_success")

    # --- NAVIGATE TO LEAVE TYPE MASTER (exact codegen) ---
    print("[ADMIN STEP 2] Navigating: Settings → Masters → Attendance → Leave Type...")

    # click settings button
    page.locator("button").filter(has_text="settings").click()
    page.wait_for_timeout(2000)

    # click Masters menuitem
    page.get_by_role("menuitem", name="Masters").click()
    page.wait_for_timeout(3000)
    take_screenshot(page, "admin_step2_masters_page")

    # click 'Attendancechevron_right' (exact codegen text)
    page.get_by_text("Attendancechevron_right").click()
    page.wait_for_timeout(2000)

    # click Leave Type Configure leave
    page.get_by_role("button", name="Leave Type Configure leave").click()
    page.wait_for_timeout(3000)
    take_screenshot(page, "admin_step2_leave_type_list")

    # --- EXPAND ROW & SET MAX DAYS (exact codegen) ---
    print("[ADMIN STEP 3] Expanding leave type row and setting Max No.of Days...")

    # expand row: page.getByRole('button').filter({ hasText: /^$/ }).nth(2).click()
    page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(2).click()
    page.wait_for_timeout(2000)
    take_screenshot(page, "admin_step3_row_expanded")

    # click 'Additional Details' (exact codegen)
    page.get_by_text("Additional Details").click()
    page.wait_for_timeout(2000)
    take_screenshot(page, "admin_step3_additional_details")

    # click & fill Max No.of Days = 2, press Enter (exact codegen)
    max_days_field = page.get_by_role("textbox", name="Max No.of Days")
    max_days_field.wait_for(state="visible", timeout=10000)
    max_days_field.click()
    max_days_field.fill(MAX_DAYS_SETTING)
    max_days_field.press("Enter")
    page.wait_for_timeout(1000)
    print(f"[ADMIN STEP 3] Max No.of Days set to {MAX_DAYS_SETTING}")
    take_screenshot(page, "admin_step3_max_days_set")

    # click Update (exact codegen)
    page.get_by_role("button", name="Update").click()
    page.wait_for_timeout(3000)

    # Capture confirmation message
    msg = capture_system_message(page)
    if msg:
        print(f"[ADMIN STEP 3] System response: {msg}")
    take_screenshot(page, "admin_step3_updated")
    print(f"[ADMIN STEP 3] [PASS] Max No.of Days updated to {MAX_DAYS_SETTING}!")

    # --- LOGOUT (exact codegen) ---
    print("[ADMIN STEP 4] Logging out admin...")

    # codegen: page.getByRole('button', { name: 'Monisha K [SSSRC018] - 12:17:' }).click()
    profile_btn = page.get_by_role("button", name=re.compile(r".*SSSRC018.*"))
    profile_btn.click()
    page.wait_for_timeout(1500)

    # click Logout menuitem
    page.get_by_role("menuitem", name="Logout").click()
    page.wait_for_timeout(3000)
    take_screenshot(page, "admin_step4_logged_out")
    print("[ADMIN STEP 4] [PASS] Admin logged out!")


# =====================================================================
#  MAIN EXECUTION
# =====================================================================

def run_masters_max_days():
    """Run the Admin Max Days configuration."""

    print("=" * 70)
    print("  Masters: Max Leave Days Configuration")
    print(f"  Set Max No.of Days = {MAX_DAYS_SETTING} in Leave Master")
    print("=" * 70)
    print(f"  Admin: {ADMIN_ID}")
    print("=" * 70)
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        try:
            print("\n" + "#" * 70)
            print(f"#  ADMIN — Set Max No.of Days = {MAX_DAYS_SETTING} in Leave Master")
            print("#" * 70)

            admin_step1_login_and_configure(page)

            print("\n" + "=" * 70)
            print(f"  [PASS] Max No.of Days successfully set to {MAX_DAYS_SETTING}")
            print(f"  Screenshots saved to: {SCREENSHOT_DIR}")
            print("=" * 70)

        except Exception as e:
            print(f"\n[FATAL ERROR] {str(e)}")
            try:
                take_screenshot(page, "fatal_error")
            except Exception:
                pass

        finally:
            try:
                take_screenshot(page, "masters_max_days_done")
            except Exception:
                pass
            browser.close()


if __name__ == "__main__":
    run_masters_max_days()
