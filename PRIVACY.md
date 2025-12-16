# Privacy Policy for ManyFold2Bambu

**Effective Date:** 2025-12-15

## 1. Introduction

This Privacy Policy describes how the **ManyFold2Bambu** browser extension ("we", "us", or "our") collects, uses, and discloses information, and what choices you have with respect to the information.

We respect your privacy and are committed to protecting it through our compliance with this policy.

## 2. No Data Collection

**We do not collect, store, or transmit any personal data.**

This extension operates entirely locally on your device. It communicates directly between your web browser and the installed Native Host application on your computer. No data is sent to our servers or any third-party servers.

## 3. Implementation Details

### How It Works

- The extension scans web pages you visit **solely** to identify 3D model files (specifically `.stl` and `.3mf` links) so that it can display an "Open in Bambu Studio" button.
- When you click the button, the file is downloaded to your local computer.
- The extension then sends a message to the locally installed **Native Host Application** (a Python script running on your machine).
- The Native Host Application launches Bambu Studio and passes the file path to it.

### Permissions Usage

We request specific permissions for the sole purpose of functionality:

- **`downloads`**: To save the model file to your computer.
- **`nativeMessaging`**: To communicate with the local Native Host script.
- **`activeTab` / `scripting`**: To inject the "Open" button into the page.
- **`webNavigation`**: To handle page changes on Single Page Applications.
- **Host Permissions (`<all_urls>`)**: To support self-hosted Manyfold instances on any domain.

## 4. Third-Party Services

We do not use any third-party analytics, tracking scripts (like Google Analytics), or advertising networks.

## 5. Changes to This Policy

We may update this privacy policy from time to time. If we make material changes, we will notify you by updating the date at the top of this policy and, where appropriate, providing notice through the extension.

## 6. Contact Us

If you have any questions about this Privacy Policy, please contact us via the support link on the Chrome Web Store listing.
