# Publishing Tunnelkey on Google Play

Everything needed for the Play Console, in the order the Console asks for it.

**All store texts (both languages) are collected in one copy-paste page:
[LISTING.md](LISTING.md).**
Text marked **Copy** can be pasted as-is.

| What | Where |
|------|-------|
| Store texts (en-US, sk) | `fastlane/metadata/android/<locale>/` — `title.txt`, `short_description.txt`, `full_description.txt`, `changelogs/100.txt` |
| App icon 512×512 | `fastlane/metadata/android/<locale>/images/icon.png` |
| Feature graphic 1024×500 | `fastlane/metadata/android/<locale>/images/featureGraphic.png` |
| Phone screenshots 1080×2160 (7) | `fastlane/metadata/android/<locale>/images/phoneScreenshots/1..7.png` |
| Privacy policy | `docs/privacy-policy.md` → published as `https://kalipsers.github.io/TunnelKey/privacy-policy.html` |
| Release bundle | `android/app/build/outputs/bundle/release/app-release.aab` |

The folder layout is fastlane's, so `fastlane supply` can upload texts and
graphics automatically later; for the first release, upload by hand.

---

## 0. Before you start

- **Organization developer account.** Google Play only accepts apps that use
  `VpnService` from *organization* accounts (needs a D-U-N-S number for
  ProIT services). A personal account can't publish Tunnelkey.
  ([Choose a developer account type](https://support.google.com/googleplay/android-developer/answer/13634885))
- **Package name:** `com.proitservices.tunnelkey` — permanent once uploaded.
- **Privacy policy online.** Enable GitHub Pages for this repository:
  *Settings → Pages → Source: Deploy from a branch → `main` / `/docs`*.
  After a minute `https://kalipsers.github.io/TunnelKey/privacy-policy.html`
  must load (the app's About dialog links to it too). Regenerate the HTML after
  editing the Markdown: `python docs/play-store/build_pages.py`.

## 1. Upload key and release build

Google Play App Signing keeps the real signing key; you sign uploads with an
*upload key*. Create it once and keep it (and its passwords) somewhere safe —
never in git.

```bash
keytool -genkeypair -v -keystore tunnelkey-upload.jks -alias upload \
  -keyalg RSA -keysize 4096 -validity 10000 \
  -dname "CN=ProIT services, O=ProIT services, C=SK"
```

Create `android/keystore.properties` (git-ignored):

```properties
storeFile=../tunnelkey-upload.jks
storePassword=…
keyAlias=upload
keyPassword=…
```

Build the bundle:

```bash
cd android
./gradlew :app:bundleRelease
```

For every later release, raise `versionCode` (and `versionName`) in
`android/app/build.gradle.kts` and add `fastlane/metadata/android/<locale>/changelogs/<versionCode>.txt`.

## 2. Create the app

*Play Console → Create app*

| Field | Value |
|-------|-------|
| App name | `Tunnelkey – 2FA VPN client` |
| Default language | English (United States) – en-US |
| App or game | App |
| Free or paid | Free |
| Declarations | Accept Developer Program Policies and US export laws |

## 3. Main store listing

*Grow → Store presence → Main store listing* (then *Add translation → Slovak* with the `sk` files)

- **App name / Short description / Full description:** from `fastlane/metadata/android/en-US/`
- **App icon, Feature graphic, Phone screenshots:** from `…/en-US/images/`
- **Video:** none
- Tablet screenshots: skip (the app is phone-first; Play shows phone screenshots on tablets)

*Store settings*

| Field | Value |
|-------|-------|
| App category | Tools |
| Tags | VPN & Proxy, Security, Productivity (pick what the Console offers) |
| Email | develop@pro-it.sk |
| Website | https://github.com/kalipsers/TunnelKey |
| Phone | optional |

## 4. App content (Policy → App content)

### Privacy policy
`https://kalipsers.github.io/TunnelKey/privacy-policy.html`

### Ads
**No**, the app does not contain ads.

### App access
Choose **All or some functionality is restricted** — reviewers need a VPN
server to connect to. Before submitting, create a reviewer package on your
Tunnelkey server (a test user on a test OpenVPN server, password + TOTP
included), save its QR code(s) as images, host them where the reviewer can open
them (or attach as instructions), and fill in:

**Copy** (adjust the placeholders):
> Tunnelkey is a client for OpenVPN servers and needs a server to connect to.
> We provide a test configuration:
> 1. Open this page on a computer: <URL of the reviewer QR code image(s)>
> 2. In the app tap the QR icon (top bar) → "Scan setup code" and scan the code.
> 3. Choose "Use an 8-digit PIN" and enter 39174826 twice (or use fingerprint).
> 4. Tap "Connect" and accept Android's VPN request. The status turns to "Protected".
> The test server only allows traffic to <test resources>. No real user data is involved.
> Alternatively, import the attached test profile with the "+" button; username: <user>, password: <pass>; the 2FA code is shown at <URL>.

### Content rating (IARC questionnaire)
- Category: **All other app types** (utility / productivity)
- Violence, blood, fear, sexuality, nudity, profanity, drugs, alcohol, tobacco, gambling, crude humour: **No**
- Users can interact or exchange content with other users: **No**
- Shares the user's physical location with other users: **No**
- Allows purchases of digital goods: **No**
- Unrestricted internet access (e.g. it's a web browser or search engine): **No**

Expected result: Everyone / PEGI 3 / USK 0.

### Target audience and content
- Target age groups: **18 and over** only
- Appeals to children: **No**

### News app
**No**

### Data safety
Tunnelkey sends nothing to ProIT services or any third party. Credentials and
the one-time code go only to the VPN server the *user* configured, through the
encrypted tunnel — that is the user's own service, not data collected by the
developer.

| Question | Answer |
|----------|--------|
| Does your app collect or share any of the required user data types? | **No** |
| Is all of the user data collected by your app encrypted in transit? | (not asked when nothing is collected) |
| Do you provide a way for users to request that their data is deleted? | (not asked) — data can be deleted in the app / by uninstalling |

Resulting label: "No data collected · No data shared with third parties".

### Government apps / Financial features / Health
- Government app: **No**
- Financial features: **None**
- Health: **No health features**

### Advertising ID
**No**, the app does not use an advertising ID. (Verified: the merged release
manifest has no `com.google.android.gms.permission.AD_ID`.)

### VpnService declaration
*App content → VpnService* (required for every app that uses `VpnService`)

| Question | Answer |
|----------|--------|
| Is VPN the core functionality of your app? | **Yes** |
| Use case | Connecting to a user- or organisation-operated OpenVPN server (remote access / enterprise VPN) |

**Copy** — description:
> Tunnelkey is an OpenVPN client. It uses VpnService only to create an encrypted
> OpenVPN (TLS) tunnel from the device to the VPN server specified in the
> user's own profile, which is operated by the user or their organisation. The
> app does not operate VPN servers, does not collect, log, inspect, modify or
> redirect user traffic, does not use the tunnel for advertising or
> monetisation, and sends no data to the developer. Traffic is encrypted from the
> device to the tunnel endpoint by the OpenVPN 3 core (TLS with mbed TLS).
> The Play listing describes the VPN usage in the section "How it uses the VPN".

### Foreground service permissions
The app declares `FOREGROUND_SERVICE_SPECIAL_USE` for the VPN service
(`foregroundServiceType="specialUse"`, subtype `vpn`).

**Copy** — description:
> The VPN connection runs in TunnelService, a VpnService that must stay in the
> foreground for as long as the user's VPN tunnel is active, so the tunnel isn't
> killed while the user relies on it. It shows an ongoing notification with the
> connection state and a Disconnect action. It starts only when the user taps
> Connect and stops when the user disconnects or the connection ends.

Video: record 20–30 s of the phone screen (Android's built-in screen recorder):
tap Connect → **Allow** notifications → accept the VPN dialog → pull down the
notification shade to show "VPN connected" with the timer and
Disconnect → tap Disconnect. Upload it unlisted (e.g. YouTube) and paste the
link.

No notification? Notifications were denied earlier: Settings → Apps →
Tunnelkey → Notifications → on (Android asks only twice, then stays silent).

### Permissions used (for your reference)
| Permission | Reason shown to reviewers if asked |
|------------|------------------|
| `INTERNET` | Connect to the VPN server |
| `CAMERA` | Scan setup QR codes; frames are analysed on-device only |
| `USE_BIOMETRIC` / `USE_FINGERPRINT` | Unlock stored secrets with fingerprint/face |
| `POST_NOTIFICATIONS` | Ongoing VPN notification |
| `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_SPECIAL_USE` | Keep the VPN tunnel running |
| `BIND_VPN_SERVICE` (service) | Required by VpnService |

## 5. Testing and release

1. *Test and release → Testing → Internal testing*: create a release, upload
   `app-release.aab`, add yourself as tester, install from the opt-in link and
   run through connect / scan / lock once more on a real phone.
2. The "12 testers for 14 days" closed-test rule applies to *personal*
   accounts created after 13 Nov 2023; organization accounts can go to
   production directly.
3. *Production → Create new release*: upload the bundle, release notes from
   `changelogs/100.txt` (both languages), countries: all (or your choice),
   start the rollout. First reviews of VPN apps can take several days.

## 6. Checklist

- [ ] Organization account verified (D-U-N-S)
- [ ] GitHub Pages enabled; privacy policy URL loads
- [ ] Upload key created and backed up; `keystore.properties` filled in
- [ ] `bundleRelease` built with the right `versionCode`
- [ ] Store listing en-US + sk filled, graphics uploaded
- [ ] App access instructions with a working reviewer configuration
- [ ] Content rating, target audience, data safety, ads, advertising ID done
- [ ] VpnService declaration submitted
- [ ] Foreground service declaration + video submitted
- [ ] Internal test install checked on a real phone
- [ ] Production release rolled out

## Regenerating the graphics

```bash
cd android
./gradlew :app:testDebugUnitTest -PplayScreenshots --tests '*PlayStoreScreenshots*'
./gradlew :app:testDebugUnitTest -PplayScreenshots -PplayLocale=sk --tests '*PlayStoreScreenshots*'
cd .. && python docs/play-store/make_graphics.py
python docs/play-store/build_listing.py   # refresh LISTING.md after editing texts
```

Screens are rendered from the real Compose UI with demo data
(`android/app/src/test/java/app/tunnelkey/PlayStoreScreenshots.kt`); captions
live in `make_graphics.py`. Fonts: Roboto (SIL Open Font License,
`docs/play-store/fonts/OFL.txt`).
