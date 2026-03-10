"""
Masters Min Leave — Admin sets Min No. of Days = 1 in Leave Master

Steps (from Playwright codegen):
  1. Login as HR Admin (SSSRC018)
  2. Navigate: Settings → Masters → Attendance → Leave Type
  3. Expand leave type row → Additional Details
  4. Set Min No. of Days = 1 → Update
  5. Logout

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


def run_masters_min_leave():
    """Admin login → Set Min No. of Days = 1 in Leave Master → Logout."""

    print("=" * 70)
    print("  Masters Min Leave — Set Min No. of Days = 1")
    print("=" * 70)
    print(f"  Admin: {ADMIN_ID}")
    print("=" * 70)
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        try:
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

            # --- EXPAND ROW & SET MIN DAYS (exact codegen) ---
            print("[ADMIN STEP 3] Expanding leave type row and setting Min No. of Days...")

            # expand row: page.getByRole('button').filter({ hasText: /^$/ }).nth(2).click()
            page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(2).click()
            page.wait_for_timeout(2000)
            take_screenshot(page, "admin_step3_row_expanded")

            # click 'Additional Details' (exact codegen — no 'note_add' prefix)
            page.get_by_text("Additional Details").click()
            page.wait_for_timeout(2000)
            take_screenshot(page, "admin_step3_additional_details")

            # click & fill Min No. of Days = 1, press Enter
            min_days_field = page.get_by_role("textbox", name="Min No. of Days")
            min_days_field.wait_for(state="visible", timeout=10000)
            min_days_field.click()
            min_days_field.fill("1")
            min_days_field.press("Enter")
            page.wait_for_timeout(1000)
            print("[ADMIN STEP 3] Min No. of Days set to 1")
            take_screenshot(page, "admin_step3_min_days_set")

            # click Update
            page.get_by_role("button", name="Update").click()
            page.wait_for_timeout(3000)

            # Capture confirmation message
            msg = capture_system_message(page)
            if msg:
                print(f"[ADMIN STEP 3] System response: {msg}")
            take_screenshot(page, "admin_step3_updated")
            print("[ADMIN STEP 3] [PASS] Min No. of Days updated to 1!")

            # --- LOGOUT (exact codegen) ---
            print("[ADMIN STEP 4] Logging out admin...")

            # codegen: page.getByRole('button', { name: 'Monisha K [SSSRC018] - 11:34:' }).click()
            # Timestamp changes every session, so match with regex
            profile_btn = page.get_by_role("button", name=re.compile(r".*SSSRC018.*"))
            profile_btn.click()
            page.wait_for_timeout(1500)

            # click Logout menuitem
            page.get_by_role("menuitem", name="Logout").click()
            page.wait_for_timeout(3000)
            take_screenshot(page, "admin_step4_logged_out")
            print("[ADMIN STEP 4] [PASS] Admin logged out!")

            print("\n" + "=" * 70)
            print("  COMPLETED — Min No. of Days set to 1 in Leave Master")
            print(f"  Screenshots saved to: {SCREENSHOT_DIR}")
            print("=" * 70)

        except Exception as e:
            print(f"\n[FATAL ERROR] {str(e)}")
            try:
                take_screenshot(page, "fatal_error")
            except Exception:
                pass

        finally:
            browser.close()


if __name__ == "__main__":
    run_masters_min_leave()
