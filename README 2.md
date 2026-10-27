# UTS Assignment 3 - Swapnil - Account Function Testing

Tests for F3 Logout (T003), F5 Edit Account (T005), F6 Change Password (T006).

## Setup (macOS)

1. Install Chrome and Python 3.12+.
2. In the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export OC_TEST_EMAIL='swapniltirpude33@gmail.com'
export OC_TEST_PASSWORD='YOUR_CURRENT_TEST_ACCOUNT_PASSWORD'
export OC_TEMP_PASSWORD='ANOTHER_DIFFERENT_TEST_PASSWORD'
python -m pytest swapnil/test_f3_logout.py swapnil/test_f5_edit_account.py swapnil/test_f6_change_password.py -v -s
```

Each test creates a fresh Chrome window and saves a screenshot in `swapnil/screenshots/`.
Screenshots contain account information. Do not commit them publicly or commit credentials.
The valid edit test restores the original first name. The password-change test tries to
restore the original password; if interrupted after the change, log in with the temporary
password and restore manually. Use a dedicated testing account, not a personal account.

Expected outcomes have not been verified by running these tests against the live site.
Capture actual pytest results for your report. The demo site may differ in validation behavior.
