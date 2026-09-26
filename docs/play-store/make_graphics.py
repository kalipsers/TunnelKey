"""Builds the Google Play graphics from the rendered app screens.

    1. Render the screens (real Compose UI, demo data):
         cd android && ./gradlew :app:testDebugUnitTest -PplayScreenshots --tests '*PlayStoreScreenshots*'
    2. python docs/play-store/make_graphics.py

Writes into fastlane/metadata/android/<locale>/images/:
  icon.png (512x512), featureGraphic.png (1024x500), phoneScreenshots/1..6.png (1080x2160)
Requires Pillow. Font: Roboto (SIL OFL, docs/play-store/fonts/).
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
RAW = Path(__file__).with_name("screens-raw")
META = ROOT / "fastlane/metadata/android"
FONT = Path(__file__).with_name("fonts") / "Roboto.ttf"
ICON_SRC = ROOT / "ios/Tunnelkey/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png"

INK = (11, 15, 20)
LINE = (32, 42, 54)
TEXT = (230, 237, 243)
MUTED = (147, 161, 176)
BRASS = (227, 169, 59)
SLATE = (90, 107, 125)
KEY = (245, 243, 238)

SCREENS = ["1_connected", "2_sign_in", "3_profiles", "4_two_factor", "5_setup_code", "6_locked"]

CAPTIONS = {
    "en-US": [
        ("Connect with one tap", "Your 2FA code is generated on the phone. No typing, no app switching."),
        ("Password + authenticator code", "Combined exactly the way your OpenVPN server expects it."),
        ("All your OpenVPN profiles", "Import any .ovpn file. Keys and certificates stay on the device."),
        ("Two-factor, per profile", "Code after or before the password, 6 or 8 digits."),
        ("Set up with one QR code", "Your admin sends the profile, sign-in and links in a single scan."),
        ("Locked with fingerprint or PIN", "Secrets never leave the phone. Weak PINs are refused."),
    ],
    "sk": [
        ("Pripojenie jedným ťuknutím", "2FA kód sa vygeneruje priamo v telefóne. Nič neprepisujete."),
        ("Heslo + overovací kód", "Spojené presne tak, ako to očakáva váš OpenVPN server."),
        ("Všetky OpenVPN profily", "Importujte ľubovoľný .ovpn súbor. Kľúče a certifikáty zostávajú v zariadení."),
        ("Dvojfaktorové overenie", "Kód za heslom alebo pred ním, 6 alebo 8 číslic."),
        ("Nastavenie jedným QR kódom", "Správca pošle profil, prihlásenie aj odkazy v jednom skenovaní."),
        ("Zamknuté odtlačkom alebo PIN", "Tajné údaje neopustia telefón. Slabé PIN kódy sú odmietnuté."),
    ],
}

FEATURE_TAGLINE = {
    "en-US": "OpenVPN with two-factor sign-in",
    "sk": "OpenVPN s dvojfaktorovým prihlásením",
}


def font(size, weight="Regular"):
    f = ImageFont.truetype(str(FONT), size)
    f.set_variation_by_name(weight)
    return f


def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=fnt) <= width:
            line = test
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def background(size):
    """Ink canvas with a faint engineering grid and a warm glow."""
    w, h = size
    img = Image.new("RGB", size, INK)
    d = ImageDraw.Draw(img)
    for x in range(0, w, 72):
        d.line([(x, 0), (x, h)], fill=(17, 22, 29))
    for y in range(0, h, 72):
        d.line([(0, y), (w, y)], fill=(17, 22, 29))
    glow = Image.new("L", size, 0)
    ImageDraw.Draw(glow).ellipse([w * 0.1, -h * 0.25, w * 0.9, h * 0.25], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(w // 6))
    img.paste(Image.new("RGB", size, (70, 52, 18)), (0, 0), glow)
    return img


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius, fill=255)
    out = Image.new("RGBA", im.size)
    out.paste(im, (0, 0), mask)
    return out


def framed_screenshot(raw, title, subtitle):
    W, H = 1080, 2160
    img = background((W, H))
    d = ImageDraw.Draw(img)

    y = 130
    fh = font(70, "Bold")
    for line in wrap(d, title, fh, W - 140):
        d.text((W / 2, y), line, font=fh, fill=TEXT, anchor="mt")
        y += 84
    y += 14
    fs = font(38)
    for line in wrap(d, subtitle, fs, W - 180):
        d.text((W / 2, y), line, font=fs, fill=MUTED, anchor="mt")
        y += 52

    # Fit the whole screen below the caption, keeping a margin at the bottom.
    top = max(y + 56, 440)
    shot_h = H - top - 90
    shot_w = min(860, int(shot_h * raw.width / raw.height))
    shot = raw.resize((shot_w, int(raw.height * shot_w / raw.width)), Image.LANCZOS)
    frame = Image.new("RGBA", (shot.width + 16, shot.height + 16), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle([0, 0, frame.width - 1, frame.height - 1], 58, fill=LINE)
    frame.paste(rounded(shot, 50), (8, 8), rounded(shot, 50))
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle(
        [(W - frame.width) / 2, top + 30, (W + frame.width) / 2, top + frame.height + 30], 58, fill=160)
    img.paste((0, 0, 0), (0, 0), shadow.filter(ImageFilter.GaussianBlur(40)))
    img.paste(frame, ((W - frame.width) // 2, top), frame)
    return img


def feature_graphic(raw, tagline):
    W, H = 1024, 500
    img = background((W, H))
    d = ImageDraw.Draw(img)

    icon = Image.open(ICON_SRC).convert("RGB").resize((112, 112), Image.LANCZOS)
    img.paste(rounded(icon, 26), (70, 60), rounded(icon, 26))
    d.text((66, 272), "Tunnelkey", font=font(84, "Bold"), fill=TEXT, anchor="ls")
    y = 322
    for line in wrap(d, tagline, font(34), 540):
        d.text((72, y), line, font=font(34), fill=MUTED, anchor="ls")
        y += 44
    d.rounded_rectangle([72, y - 10, 72 + 150, y + 40], 12, fill=(58, 44, 16))
    d.text((72 + 75, y + 15), "Open source", font=font(22, "Medium"), fill=(255, 223, 166), anchor="mm")

    # Top of the "connected" screen in a phone-like frame, cropped by the edge.
    shot = raw.crop((0, 0, raw.width, int(raw.width * 1.25))).resize((330, 412), Image.LANCZOS)
    frame = Image.new("RGBA", (shot.width + 12, shot.height + 12), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle([0, 0, frame.width - 1, frame.height + 40], 40, fill=LINE)
    frame.paste(rounded(shot, 34), (6, 6), rounded(shot, 34))
    img.paste(frame, (W - frame.width - 70, 70), frame)
    return img


def main():
    raws = {name: Image.open(RAW / f"{name}.png").convert("RGB") for name in SCREENS}
    icon = Image.open(ICON_SRC).convert("RGBA").resize((512, 512), Image.LANCZOS)
    for locale, captions in CAPTIONS.items():
        images = META / locale / "images"
        (images / "phoneScreenshots").mkdir(parents=True, exist_ok=True)
        icon.save(images / "icon.png")
        feature_graphic(raws["1_connected"], FEATURE_TAGLINE[locale]).save(images / "featureGraphic.png")
        for i, (name, (title, subtitle)) in enumerate(zip(SCREENS, captions), start=1):
            framed_screenshot(raws[name], title, subtitle).save(images / "phoneScreenshots" / f"{i}.png")
        print(f"{locale}: icon, featureGraphic, {len(SCREENS)} screenshots")


if __name__ == "__main__":
    main()
