"""
Masters Negative Leave — HR Admin sets Negative Leave to Disabled

Steps:
  1. Login as HR Admin (SSSRC018)
  2. Navigate to Settings → Masters → Attendance → Leave
  3. Open 5th leave type row → Additional Details
  4. Uncheck "Negative Leaves can be Accrued" checkbox (Disable it)
  5. Click Update
  6. Logout

URL:  https://qa-current.247hrmstaging.com:8452
"""

import os
import sys
import io
from datetime import datetime
from playwright.sync_api import sync_playwright

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ========== CONFIGURATION ==========
URL = "https://qa-current.247hrmstaging.com:8452"

# HR Admin credentials
ADMIN_ID       = "SSSRC018"
ADMIN_PASSWORD = "sys"

# Screenshots go into the same folder as this script
SCREENSHOT_DIR = os.path.dirname(os.path.abspath(__file__))
# ====================================


# ──────────────────────────────────────────────────────────────
# UTILITY HELPERS
# ──────────────────────────────────────────────────────────────

def take_screenshot(page, name):
    """Save a timestamped screenshot and print its path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
    page.screenshot(path=filepath)
    print(f"[SCREENSHOT] Saved: {filepath}")
    return filepath


def capture_system_message(page):
    """Try to capture any toast / snackbar / alert message from the UI."""
    selectors = [
        "simple-snack-bar",
        ".mat-snack-bar-container",
        ".cdk-overlay-container .mat-snack-bar-container",
        ".mat-mdc-snack-bar-container",
        "mat-snack-bar-container",
        ".toast-message",
        "alertdialog",
        "[role='alert']",
    ]
    for selector in selectors:
        try:
            el = page.locator(selector).first
            if el.is_visible(timeout=3000):
                msg = el.inner_text().strip()
                if msg:
                    return msg
        except Exception:
            continue
    return None


# ──────────────────────────────────────────────────────────────
# HR ADMIN FUNCTIONS
# ──────────────────────────────────────────────────────────────

def admin_login(page):
    """Login as HR Admin (SSSRC018)."""
    print("\n[STEP 1] Navigating to Login page...")
    page.goto(f"{URL}/#/login")
    page.get_by_role("textbox", name="Employee Id").wait_for(state="visible", timeout=15000)
    page.get_by_role("textbox", name="Employee Id").fill(ADMIN_ID)
    page.get_by_role("textbox", name="Password").fill(ADMIN_PASSWORD)
    print("[STEP 1] Clicking LOG IN...")
    page.get_by_role("button", name="LOG IN").click()
    page.wait_for_url("**/dashboard/welcomePage*", timeout=60000)
    page.wait_for_timeout(3000)
    print("[STEP 1] [PASS] Admin login successful!")
    take_screenshot(page, "master_step1_login_success")


def navigate_to_leave_master(page):
    """Navigate: Settings gear → Masters → Attendance → Leave."""
    print("\n[STEP 2] Navigating to Masters → Leave settings...")

    print("[STEP 2a] Clicking Settings gear button...")
    settings_btn = page.locator("button").filter(has_text="settings")
    settings_btn.wait_for(state="visible", timeout=10000)
    settings_btn.click()
    page.wait_for_timeout(2000)
    take_screenshot(page, "master_step2a_settings_menu")

    print("[STEP 2b] Clicking 'Masters' menu item...")
    page.get_by_role("menuitem", name="Masters").click()
    page.wait_for_timeout(3000)
    take_screenshot(page, "master_step2b_masters_page")

    print("[STEP 2c] Clicking 'Attendance' section...")
    page.get_by_text("Attendancechevron_right").click()
    page.wait_for_timeout(2000)
    take_screenshot(page, "master_step2c_attendance_expanded")

    print("[STEP 2d] Clicking 'Leave' subsection...")
    page.get_by_text("beach_accessLeave").click()
    page.wait_for_timeout(3000)
    take_screenshot(page, "master_step2d_leave_list")

    print("[STEP 2] [PASS] Arrived at Leave Master list page.")


def open_leave_type_and_additional_details(page):
    """Click edit on 5th leave type row, then open Additional Details tab."""
    print("\n[STEP 3] Opening leave type edit (5th row)...")

    edit_btn = page.locator(
        "tr:nth-child(5) > .mat-cell.cdk-cell.cdk-column-action > button"
    ).first
    edit_btn.wait_for(state="visible", timeout=10000)
    edit_btn.click()
    page.wait_for_timeout(3000)
    take_screenshot(page, "master_step3_leave_type_edit")

    print("[STEP 3] Clicking 'Additional Details' tab...")
    page.get_by_text("note_addAdditional Details").click()
    page.wait_for_timeout(2000)
    take_screenshot(page, "master_step3_additional_details")

    print("[STEP 3] [PASS] Additional Details tab opened.")


def set_negative_leave_disabled(page):
    """
    Find and uncheck the Negative Leave checkbox in the Additional Details section.
    Scrolls down to reveal the setting if below the fold.
    Returns True if setting was found and configured, False otherwise.
    """
    print("\n[STEP 4] Looking for 'Negative Leave' checkbox...")
    page.wait_for_timeout(2000)

    # Scroll down within the dialog to reveal all settings
    dialog = page.locator("mat-dialog-container").first
    try:
        dialog.evaluate("el => el.scrollTop = el.scrollHeight")
        page.wait_for_timeout(1500)
        take_screenshot(page, "master_step4_scrolled_down")
    except Exception:
        pass

    for scroll_target in [".mat-dialog-content", ".mat-tab-body-content", ".mat-tab-body-wrapper"]:
        try:
            scroller = page.locator(scroll_target).first
            if scroller.is_visible(timeout=1000):
                scroller.evaluate("el => el.scrollTop = el.scrollHeight")
                page.wait_for_timeout(1000)
        except Exception:
            pass

    take_screenshot(page, "master_step4_after_scroll")

    # Strategy 1: Find checkbox by text containing 'Negative'
    try:
        checkbox = page.locator("mat-checkbox").filter(has_text="Negative").first
        if checkbox.is_visible(timeout=3000):
            checkbox.scroll_into_view_if_needed()
            page.wait_for_timeout(500)

            cls = checkbox.get_attribute("class") or ""
            is_checked = "mat-checkbox-checked" in cls

            print(f"[STEP 4] Found 'Negative' checkbox by text. Checked={is_checked}")
            take_screenshot(page, "master_step4_negative_checkbox_found")

            if is_checked:
                print("[STEP 4] Clicking to UNCHECK (Disable Negative Leave)...")
                checkbox.locator(".mat-checkbox-inner-container").click()
                page.wait_for_timeout(1500)
                take_screenshot(page, "master_step4_neg_unchecked")
                print("[STEP 4] [PASS] Negative Leave unchecked (Disabled).")
            else:
                print("[STEP 4] [INFO] Already unchecked (Disabled). No change needed.")
                take_screenshot(page, "master_step4_neg_already_off")

            return True
    except Exception as e:
        print(f"[STEP 4] Text-based checkbox strategy failed: {e}")

    # Strategy 2: Find label with 'Negative' and look for nearby checkbox
    try:
        neg_text = page.get_by_text("Negative", exact=False).first
        if neg_text.is_visible(timeout=3000):
            neg_text.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            take_screenshot(page, "master_step4_negative_text_visible")

            parent_row = neg_text.locator("xpath=ancestor::div[contains(@class,'row') or contains(@class,'section') or contains(@class,'form-group') or self::div][1]")
            checkbox = parent_row.locator("mat-checkbox").first
            if checkbox.is_visible(timeout=2000):
                cls = checkbox.get_attribute("class") or ""
                is_checked = "mat-checkbox-checked" in cls
                print(f"[STEP 4] Found checkbox near 'Negative' text. Checked={is_checked}")

                if is_checked:
                    print("[STEP 4] Clicking to UNCHECK...")
                    checkbox.locator(".mat-checkbox-inner-container").click()
                    page.wait_for_timeout(1500)
                    print("[STEP 4] [PASS] Negative Leave unchecked.")
                else:
                    print("[STEP 4] [INFO] Already unchecked.")

                take_screenshot(page, "master_step4_neg_configured")
                return True
    except Exception as e:
        print(f"[STEP 4] Nearby checkbox strategy failed: {e}")

    # Strategy 3: Scan all checkboxes
    try:
        all_checkboxes = page.locator("mat-checkbox").all()
        print(f"[STEP 4] Found {len(all_checkboxes)} checkboxes on page. Listing all:")
        for i, cb in enumerate(all_checkboxes):
            try:
                cb.scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                cb_text = cb.inner_text().strip()
                cb_class = cb.get_attribute("class") or ""
                is_checked = "mat-checkbox-checked" in cb_class
                print(f"  [{i}] Text='{cb_text}' Checked={is_checked}")

                if "negative" in cb_text.lower() or "neg" in cb_text.lower():
                    print(f"[STEP 4] Found Negative Leave checkbox at index {i}!")
                    if is_checked:
                        cb.locator(".mat-checkbox-inner-container").click()
                        page.wait_for_timeout(1500)
                        print("[STEP 4] [PASS] Unchecked.")
                    else:
                        print("[STEP 4] [INFO] Already unchecked.")
                    take_screenshot(page, "master_step4_neg_found_by_scan")
                    return True
            except Exception:
                pass
    except Exception:
        pass

    # Strategy 4: Try mat-slide-toggle
    try:
        toggle = page.locator("mat-slide-toggle").filter(has_text="Negative").first
        if toggle.is_visible(timeout=2000):
            toggle.scroll_into_view_if_needed()
            cls = toggle.get_attribute("class") or ""
            is_checked = "mat-checked" in cls
            print(f"[STEP 4] Found 'Negative' toggle. Checked={is_checked}")
            if is_checked:
                toggle.click()
                page.wait_for_timeout(1500)
                print("[STEP 4] [PASS] Toggle switched OFF.")
            else:
                print("[STEP 4] [INFO] Toggle already OFF.")
            take_screenshot(page, "master_step4_toggle_configured")
            return True
    except Exception:
        pass

    print("[STEP 4] [WARNING] Could not find Negative Leave checkbox.")
    take_screenshot(page, "master_step4_not_found")
    return False


def save_master_settings(page):
    """Click Update button on the leave type edit page."""
    print("\n[STEP 5] Clicking Update button...")

    try:
        update_btn = page.get_by_role("button", name="Update")
        update_btn.wait_for(state="visible", timeout=5000)
        update_btn.click()
        page.wait_for_timeout(3000)

        msg = capture_system_message(page)
        if msg:
            print(f"[STEP 5] System response: {msg}")

        take_screenshot(page, "master_step5_settings_saved")
        print("[STEP 5] [PASS] Settings updated!")
        return True
    except Exception as e:
        print(f"[STEP 5] Update button click failed: {e}")

    for name in ["Save", "Submit", "Apply", "Save Changes", "UPDATE", "SAVE"]:
        try:
            btn = page.get_by_role("button", name=name)
            if btn.is_visible(timeout=1500) and btn.is_enabled():
                print(f"[STEP 5] Clicking fallback '{name}' button...")
                btn.click()
                page.wait_for_timeout(3000)
                msg = capture_system_message(page)
                if msg:
                    print(f"[STEP 5] System response: {msg}")
                take_screenshot(page, "master_step5_settings_saved")
                print("[STEP 5] [PASS] Settings saved!")
                return True
        except Exception:
            continue

    print("[STEP 5] [WARNING] No Update/Save button found.")
    take_screenshot(page, "master_step5_no_save_btn")
    return False


def admin_logout(page):
    """Logout from the HR admin session using profile menu → Logout."""
    print("\n[STEP 6] Logging out from Admin session...")

    try:
        profile_btn = page.locator("button").filter(has_text=ADMIN_ID).first
        if profile_btn.is_visible(timeout=5000):
            print("[STEP 6] Clicking profile button...")
            profile_btn.click()
            page.wait_for_timeout(1500)
        else:
            print("[STEP 6] Profile button not found by ID, trying generic header button...")
            header_btn = page.locator("header button, .navbar button, .toolbar button, mat-toolbar button").last
            if header_btn.is_visible(timeout=3000):
                header_btn.click()
                page.wait_for_timeout(1500)
    except Exception as e:
        print(f"[STEP 6] Profile click failed: {e}")

    try:
        page.get_by_role("menuitem", name="Logout").click()
        page.wait_for_timeout(4000)
        print("[STEP 6] [PASS] Logged out successfully.")
        take_screenshot(page, "master_step6_logged_out")
        return
    except Exception as e:
        print(f"[STEP 6] Menuitem Logout failed: {e}")

    try:
        logout_item = page.get_by_text("Logout", exact=False).filter(visible=True).first
        if logout_item.is_visible(timeout=3000):
            logout_item.click()
            page.wait_for_timeout(4000)
            print("[STEP 6] [PASS] Logged out (text fallback).")
            take_screenshot(page, "master_step6_logged_out")
            return
    except Exception:
        pass

    print("[STEP 6] Forcing navigation to login page...")
    page.goto(f"{URL}/#/login")
    page.wait_for_timeout(3000)
    take_screenshot(page, "master_step6_logout_fallback")
    print("[STEP 6] [INFO] Navigated to login page (session ended).")


# ──────────────────────────────────────────────────────────────
# MAIN RUNNER
# ──────────────────────────────────────────────────────────────

def run_masters_negative_leave():
    print("=" * 70)
    print("  Masters: Set Negative Leave = Disabled")
    print("  HR Admin (SSSRC018) → Settings → Masters → Leave → Additional Details")
    print("  Uncheck 'Negative Leaves can be Accrued' → Update → Logout")
    print("=" * 70)
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        setting_configured = False

        try:
            admin_login(page)
            navigate_to_leave_master(page)
            open_leave_type_and_additional_details(page)
            setting_configured = set_negative_leave_disabled(page)
            save_master_settings(page)
            admin_logout(page)

            # Final result
            print("\n" + "=" * 70)
            print("  RESULT")
            print("=" * 70)
            if setting_configured:
                print("  [PASS] Negative Leave setting = Disabled (configured successfully)")
                take_screenshot(page, "master_FINAL_PASS")
            else:
                print("  [FAIL] Could not locate or configure the Negative Leave setting")
                take_screenshot(page, "master_FINAL_FAIL")
            print(f"  Screenshots saved to: {SCREENSHOT_DIR}")
            print("=" * 70)

        except Exception as e:
            print(f"\n[FATAL ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            try:
                take_screenshot(page, "master_FATAL_ERROR")
            except Exception:
                pass
        finally:
            browser.close()


if __name__ == "__main__":
    run_masters_negative_leave()
