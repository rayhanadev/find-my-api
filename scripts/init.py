import os
import sys
from pyicloud import PyiCloudService

from dotenv import load_dotenv

load_dotenv()


def main():
    APPLE_ICLOUD_ID = os.environ.get("APPLE_ICLOUD_ID")
    APPLE_ICLOUD_PASSWORD = os.environ.get("APPLE_ICLOUD_PASSWORD")
    APPLE_DEVICE_NAME = os.environ.get("APPLE_DEVICE_NAME")

    if not APPLE_ICLOUD_ID or not APPLE_ICLOUD_PASSWORD:
        print(
            "Environment variables APPLE_ICLOUD_ID and APPLE_ICLOUD_PASSWORD must be set"
        )
        sys.exit(1)

    if not APPLE_DEVICE_NAME:
        print("Environment variable APPLE_DEVICE_NAME must be set")
        sys.exit(1)

    cookie_directory = os.path.join(os.getcwd(), ".icloud")
    os.makedirs(cookie_directory, exist_ok=True)

    print("Beginning iCloud login…")

    try:
        api = PyiCloudService(
            APPLE_ICLOUD_ID, APPLE_ICLOUD_PASSWORD, cookie_directory=cookie_directory
        )

        if api.requires_2fa:
            print("Two‑factor authentication required.")
            code = input("Enter the 6‑digit code sent to a trusted device: ").strip()
            if not api.validate_2fa_code(code):
                print("Failed to verify 2FA code.")
                sys.exit(1)

            if not api.is_trusted_session:
                print("Marking session as trusted…")
                if not api.trust_session():
                    print(
                        "Failed to trust this session. You may be prompted again soon."
                    )
        elif api.requires_2sa:
            print("Two‑step authentication required.")
            devices = api.trusted_devices
            for i, device in enumerate(devices):
                device_name = (
                    device.get("deviceName") or f"SMS → {device.get('phoneNumber')}"
                )
                print(f"  [{i}] {device_name}")
            choice = input(f"Select a device (0–{len(devices) - 1}): ").strip()
            try:
                idx = int(choice)
                selected = devices[idx]
            except (ValueError, IndexError):
                print("Invalid selection.")
                sys.exit(1)

            if not api.send_verification_code(selected):
                print("Failed to send verification code to the selected device.")
                sys.exit(1)

            code = input("Enter the verification code you received: ").strip()
            if not api.validate_verification_code(selected, code):
                print("Failed to verify the 2SA code.")
                sys.exit(1)

            print("Two‑step authentication complete.")
        else:
            print("No 2FA/2SA required. Login succeeded.")

        print("iCloud authentication successful. Session cookie saved to '.icloud/'.")
    except Exception as e:
        print(f"Failed to authenticate to iCloud: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
