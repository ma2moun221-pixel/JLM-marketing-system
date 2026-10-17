#!/usr/bin/env bash
# تثبيت الأدوات المجانية المطلوبة للمونتاج: ffmpeg + خطوط عربية + إيموجي ملوّن.
# آمن للتشغيل أكثر من مرة (idempotent). يعمل بلا صلاحيات root عبر مسار محلي.
set -uo pipefail

LOCAL_BIN="${HOME}/.local/bin"
FONT_DIR="${HOME}/.local/share/fonts"
mkdir -p "$LOCAL_BIN" "$FONT_DIR"

have() { command -v "$1" >/dev/null 2>&1; }
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }

# ---------- 1) ffmpeg ----------
install_ffmpeg_apt() {
  have apt-get || return 1
  say "محاولة التثبيت عبر apt..."
  apt-get update -qq >/dev/null 2>&1
  apt-get install -y --no-install-recommends ffmpeg >/dev/null 2>&1
  have ffmpeg
}

install_ffmpeg_static() {
  # بناء ثابت (static) من johnvansickle — يتضمّن libass و fontconfig و libmp3lame.
  say "محاولة تنزيل بناء ffmpeg ثابت..."
  local url="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
  local tmp; tmp="$(mktemp -d)"
  curl -fsSL --retry 3 "$url" -o "$tmp/ff.tar.xz" 2>/dev/null || return 1
  tar -xJf "$tmp/ff.tar.xz" -C "$tmp" 2>/dev/null || return 1
  local d; d="$(find "$tmp" -maxdepth 1 -type d -name 'ffmpeg-*' | head -1)"
  [ -n "$d" ] || return 1
  install -m755 "$d/ffmpeg" "$d/ffprobe" "$LOCAL_BIN/" || return 1
  rm -rf "$tmp"
  export PATH="$LOCAL_BIN:$PATH"
  have ffmpeg
}

install_ffmpeg_pip() {
  # ملاذ أخير: البناء المرفق مع imageio-ffmpeg (قد لا يدعم libass).
  have python3 || return 1
  say "محاولة التثبيت عبر pip (imageio-ffmpeg)..."
  python3 -m pip install --quiet --user imageio-ffmpeg >/dev/null 2>&1 || return 1
  local p; p="$(python3 -c 'import imageio_ffmpeg,sys; sys.stdout.write(imageio_ffmpeg.get_ffmpeg_exe())' 2>/dev/null)" || return 1
  [ -x "$p" ] || return 1
  ln -sf "$p" "$LOCAL_BIN/ffmpeg"
  export PATH="$LOCAL_BIN:$PATH"
  warn "هذا البناء قد لا يدعم فلتر ass — الكابشن العربي قد لا يعمل. فضّل apt أو البناء الثابت."
  have ffmpeg
}

if have ffmpeg && have ffprobe; then
  say "ffmpeg موجود: $(ffmpeg -version 2>/dev/null | head -1)"
else
  install_ffmpeg_apt || install_ffmpeg_static || install_ffmpeg_pip || {
    warn "فشل تثبيت ffmpeg بكل الطرق. ثبّته يدويًا: https://ffmpeg.org/download.html"
  }
fi

# ---------- 2) التحقّق من دعم libass (ضروري للعربية) ----------
if have ffmpeg; then
  if ffmpeg -hide_banner -filters 2>/dev/null | grep -qE '^\s*\S*\s+ass\s'; then
    say "فلتر ass مدعوم ✅ (الكابشن العربي سيعمل بتشكيل صحيح)"
  else
    warn "فلتر ass غير مدعوم في هذا البناء — الكابشن العربي سيُقطَّع."
    warn "أعد التثبيت ببناء يدعم libass: apt-get install ffmpeg، أو البناء الثابت."
  fi
fi

# ---------- 3) الخطوط ----------
fonts_present() { fc-list 2>/dev/null | grep -qi "$1"; }

if have apt-get; then
  apt-get install -y --no-install-recommends fonts-noto-core fonts-noto-color-emoji >/dev/null 2>&1
fi

# خطوط عربية للعناوين من Google Fonts (رخصة SIL OFL — مجانية للاستخدام التجاري)
# raw.githubusercontent.com وليس github.com/.../raw — الثاني يعيد 403 خلف كثير من الوكلاء
GF_BASE="https://raw.githubusercontent.com/google/fonts/main/ofl"
declare -A GFONTS=(
  ["Cairo"]="$GF_BASE/cairo/Cairo%5Bslnt%2Cwght%5D.ttf"
  ["Tajawal"]="$GF_BASE/tajawal/Tajawal-Bold.ttf"
  ["Almarai"]="$GF_BASE/almarai/Almarai-ExtraBold.ttf"
)
for name in "${!GFONTS[@]}"; do
  if fonts_present "$name"; then
    say "الخط $name موجود"
  else
    say "تنزيل الخط $name..."
    curl -fsSL --retry 3 "${GFONTS[$name]}" -o "$FONT_DIR/${name}.ttf" 2>/dev/null \
      && say "تم: $name" \
      || warn "تعذّر تنزيل $name (لا اتصال؟) — سيُستخدم خط بديل"
  fi
done

have fc-cache && fc-cache -f "$FONT_DIR" >/dev/null 2>&1

# ---------- 4) تقرير نهائي ----------
echo
say "الحالة النهائية:"
printf '  ffmpeg  : %s\n'  "$(have ffmpeg  && ffmpeg -version 2>/dev/null | head -1 | cut -c1-60 || echo 'غير مثبّت ❌')"
printf '  ffprobe : %s\n'  "$(have ffprobe && echo 'موجود ✅' || echo 'غير مثبّت ❌')"
printf '  python3 : %s\n'  "$(have python3 && python3 --version || echo 'غير مثبّت ❌')"
echo "  خطوط عربية متاحة:"
fc-list :lang=ar family 2>/dev/null | tr ',' '\n' | sort -u | sed 's/^/    - /' | head -10
[ -z "$(fc-list :lang=ar 2>/dev/null)" ] && warn "لا يوجد خط عربي — الكابشن سيظهر مربّعات."
echo
say 'أضف هذا لمسارك إن ثبّتنا محليًا:  export PATH="$HOME/.local/bin:$PATH"'
