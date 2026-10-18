# برومبت أسلوب الفيديو: "السيارة تطير" (Flying Car POV – AI Reveal)

> المرجع: `Chris_Ashley.mp4` (‏13.7 ثانية، عمودي 9:16)
> الغرض: عندما يرسل المستخدم فيديو جديداً، ألصق هذا الملف كاملاً كتعليمات، ثم نفّذ الخطوات حرفياً.

---

## 1) البرومبت الرئيسي (انسخه لي مع الفيديو الجديد)

```
أنت محرر فيديو قصير (Reels/TikTok/Shorts). أرفقت لك فيديو خاص بي.
أعد مونتاجه بنفس أسلوب الفيديو المرجعي "Flying Car POV" الموصوف في
video-style-prompts/flying-car-pov.md، بهذه القواعد:

1. حافظ على كل ما يخصني: وجهي، جسمي، ملابسي، حركاتي، السيارة من الداخل،
   ألوانها وتفاصيلها، الصوت إن طلبت ذلك. ممنوع تغيير الشخص أو استبداله.
2. الذكاء الاصطناعي يغيّر "العالم خارج النوافذ فقط" + إضاءة المقصورة لتطابقه.
3. البنية: ~60% لقطات حقيقية كما هي ← ~10% وميض إقلاع أبيض ← ~30% طيران
   (سماء ثم مدينة من الأعلى).
4. نص علوي ثابت من أول فريم لآخر فريم بصيغة ميم: "Me when ..." / "أنا لما ...".
5. موسيقى فقط بدون تعليق صوتي، والإقلاع على ضربة إيقاع واضحة.
6. التصدير: 1080x1920، 30fps، H.264، AAC، المدة 10–15 ثانية.
نص الكابشن: [اكتب النص هنا أو اتركه لي لأقترح]
الموسيقى: [ارفع ملف الموسيقى / أو "احتفظ بالصوت الأصلي"]
```

---

## 2) تحليل الفيديو المرجعي

### المواصفات التقنية
| البند | القيمة |
|---|---|
| الأبعاد | 720×1280 (9:16 عمودي) |
| معدل الإطارات | 30fps ثابت |
| المدة | 13.67 ثانية (فيديو) / 13.79 (صوت) |
| الترميز | H.264 بمعدل ~1.34Mbps، صوت AAC ستيريو 44.1kHz ~71kbps |
| الصوت | موسيقى فقط بلا كلام؛ متوسط −12.4dB وأعلى قمة −3.1dB؛ قطع عند 16kHz (صوت منصة مضغوط) |

### الكاميرا والتصوير (أهم عنصر في "الشكل")
- **كاميرا 360°** (نوع Insta360 X) مثبتة في **منتصف السقف خلف المقعدين الأماميين** بارتفاع عالٍ.
- معاد تأطيرها (Reframe) بعدسة **عين سمكة واسعة جداً (~150°+)** بحيث يظهر في كادر واحد:
  السقف الزجاجي أعلى الكادر، السائق يسار من الخلف، المقعد الأبيض الفارغ يمين، الشاشة
  الوسطى، الزجاج الأمامي، وحتى أرضية/مقاعد خلفية أسفل الكادر (انحناء قوي على الأطراف).
- **لقطة واحدة متصلة بلا أي قطع** (فحص Scene detection لم يجد أي قطع).
- الكاميرا "تتنفس": دوران بطيء في الاتجاه (Yaw) وميل خفيف (Dutch roll) بين ~4.0–4.5ث
  وخلال الإقلاع — إحساس طفو، ليس اهتزازاً.
- السائق يتصرّف بطبيعية تماماً (يمسك المقود، يلتفت للكاميرا عند 0.5ث) ← سرّ الكوميديا: هدوءه مقابل المستحيل.

### الخط الزمني (Beat sheet)
| الوقت | ما يحدث | ملاحظة تحرير |
|---|---|---|
| 0.0 – 8.2ث | قيادة حقيقية على طريق سريع، سيارات ولافتات خضراء (≈7.5ث) | فوتج أصلي بدون لمس |
| 8.2 – 9.6ث | النوافذ "تحترق" للأبيض/النعناعي (Overexposure bloom) ← لحظة الإقلاع | يقع على ضربة إيقاع ≈8.45ث |
| 9.6 – 11.8ث | النوافذ لا تُظهر إلا سماء زرقاء ← السيارة في الجو تصعد | السائق مستمر بنفس الحركات |
| ≈11.6ث | هبوط تعريض لحظي (ظل أزرق داكن على المقصورة) | كأنها تمر بغيمة/ظل |
| 12.0 – 13.7ث | من الزجاج الأمامي والسقف: **أبراج وسط مدينة من الأعلى** + أشجار وأحياء تحتها | الكشف الكبير عند ضربة ≈12.28ث، ينتهي مفتوحاً بدون خاتمة |

### طريقة صنع المؤثر بالذكاء الاصطناعي (الاستنتاج)
- المقصورة والسائق **ثابتان ومتسقان** طوال المقطع (نفس الملابس، الإضاءة، حركات اليد) ←
  هذا **Video-to-Video / Inpainting للنوافذ** وليس توليد فيديو من الصفر.
- المتغيّر الوحيد: المشهد الخارجي من النوافذ + لون الضوء الداخل للمقصورة.
- الانتقال مُخفى داخل **وميض تعريض أبيض** (نفس شكل خروج الكاميرا من نفق للشمس)، فلا يرى
  المشاهد نقطة التبديل بين الحقيقي والمولَّد.
- أدوات تعطي هذه النتيجة: Runway Aleph / Luma Ray "Modify Video" / Kling (Video-to-Video
  أو Elements) / Higgsfield. البديل: توليد Image-to-Video من **آخر فريم حقيقي** ثم وصله بالوميض.

### النص (الكابشن)
- النص: `Me when I'm already 77 minutes late to work while driving the Tesla Roadster`
- صيغة ميم: "Me when + موقف يومي مبالغ + رقم محدد غريب (77) + اسم المنتج".
  النكتة مبنية على وعد "تسلا رودستر الطائرة".
- ثابت من الفريم الأول للأخير، بدون حركة أو ظهور تدريجي.
- المكان: **وسط أعلى الكادر**، يبدأ عند ~15% من الارتفاع وينتهي ~27% (فوق السقف الزجاجي، بعيداً عن وجه السائق ومنطقة واجهة التطبيق).
- الشكل: خط Sans ضيق (Condensed) يشبه خط تيك توك "Classic"، **أبيض** بظل أسود رفيع/حدّ خفيف، محاذاة وسط، 3 أسطر، حجم ≈ 4.3% من ارتفاع الكادر (≈ 82px على 1920).

### اللون
- طبيعي، ساطع، مائل للبرودة قليلاً؛ المقصورة البيضاء قريبة من الاحتراق (هذا مقبول ومطلوب للوميض).
- بدون LUT سينمائي ولا تحبيب. مشاهد السماء والمدينة يجب أن تطابق نفس السطوع ودرجة الحرارة.

### الصوت
- موسيقى ترند حماسية/درامية بإيقاع ≈ 85 BPM (ضربات كل ~0.7ث) من أول ثانية.
- لا تعليق صوتي، لا مؤثرات واضحة. لا قطع على الإيقاع (لأن اللقطة واحدة) — فقط **الإقلاع والكشف** يقعان على ضربات.

---

## 3) خطوات التنفيذ على فيديو المستخدم

### أ. الفحص
```bash
V=input.mp4
ffprobe -v error -show_format -show_streams "$V"
ffmpeg -i "$V" -vf "fps=2,scale=240:-1,drawtext=text='%{pts\:hms}':x=5:y=5:fontsize=18:fontcolor=yellow:box=1:boxcolor=black,tile=7x3" -frames:v 1 sheet.jpg
ffmpeg -i "$V" -vf "select='gt(scene,0.25)',showinfo" -f null - 2>&1 | grep pts_time   # القطعات
```
حدّد: أين الشخص؟ هل اللقطة داخل سيارة/غرفة/مكتب؟ ما الذي يظهر من النوافذ؟ أفضل 10–15ث متصلة؟
**تكييف الفكرة إن لم تكن سيارة:** المبدأ نفسه = "داخل ثابت وطبيعي + خارج يتحول لمستحيل"
(مكتب يطير فوق المدينة، مصعد يخرج للفضاء، غرفة تحت الماء...).

### ب. التجهيز
```bash
# قص وتوحيد: 1080x1920، 30fps
ffmpeg -ss START -to END -i "$V" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30" -c:v libx264 -crf 16 -preset slow -an base.mp4
# إن كان الفيديو 360 خام (equirectangular): إعادة تأطير بعين سمكة
ffmpeg -i raw360.mp4 -vf "v360=e:fisheye:ih_fov=360:iv_fov=180:h_fov=190:v_fov=190:pitch=-25,crop=ih*9/16:ih,scale=1080:1920" reframed.mp4
```
- نقطة الإقلاع = عند ~60% من المدة، على أقرب ضربة إيقاع.
- استخرج **آخر فريم قبل الإقلاع** كصورة مرجعية: `ffmpeg -ss T_LIFT -i base.mp4 -frames:v 1 lift.png`

### ج. توليد الجزء المستحيل بالذكاء الاصطناعي
قسّم: `real.mp4` (0 → T_LIFT) و `ai_src.mp4` (T_LIFT → النهاية) وأرسل الثاني لأداة Video-to-Video.

**برومبت Video-to-Video (إنجليزي — الأدوات تفهمه أفضل):**
```
Keep the car interior, the driver, his face, clothes, hands and every movement
exactly identical to the input video. Do not change the person or the cabin.
Only replace what is visible through the windshield, side windows and glass roof:
the car smoothly lifts off the highway and flies upward into a clear blue sky,
then cruises high above a sunny modern downtown skyline with skyscrapers,
trees and city blocks far below. Bright daylight, realistic, consistent with a
360 fisheye action camera mounted on the ceiling. Cabin lighting subtly shifts
to match the open sky. Photorealistic, no text, no warping of the interior.
```
**برومبت سلبي:** `face change, different person, extra fingers, warped steering wheel, melting interior, text, logo, cartoon, blur`

**البديل (Image-to-Video من lift.png):**
```
Static ceiling-mounted 360 fisheye camera inside the car. The driver keeps driving
calmly. Through all windows the road falls away as the car rises into the sky,
then flies over a city skyline. Interior and driver unchanged, slow gentle camera drift.
```
ولّد 2–4 نسخ واختر الأكثر ثباتاً للوجه واليدين.

### د. الوصل بوميض الإقلاع
```bash
# وميض أبيض 0.4ث عند نقطة الوصل يخفي التبديل
ffmpeg -i real.mp4 -i ai.mp4 -filter_complex "\
[0:v]fps=30,format=yuv420p,setpts=PTS-STARTPTS[a];[1:v]scale=1080:1920,fps=30,format=yuv420p,setpts=PTS-STARTPTS[b];\
[a][b]xfade=transition=fadewhite:duration=0.4:offset=REAL_DUR_MINUS_0.4[v]" -map "[v]" -c:v libx264 -crf 16 joined.mp4
```
ثم طابق اللون: `eq=brightness=..:saturation=..` أو `colorbalance` على جزء الـ AI حتى يطابق الحقيقي.

### هـ. الكابشن
- إنجليزي: drawtext بخط Condensed (مثلاً Oswald Light / Roboto Condensed / Bebas للخيار الأعرض).
- **عربي: استخدم فلتر `subtitles`/`ass` (libass يشكّل الحروف العربية صحيحاً) وليس drawtext.**
  خطوط مقترحة: Cairo / Tajawal / IBM Plex Sans Arabic.
```bash
# ملف caption.ass: Alignment=8 (أعلى وسط)، MarginV≈290 على 1920، أبيض، Outline=1، Shadow=1
ffmpeg -i joined.mp4 -i music.mp3 -filter_complex "[0:v]ass=caption.ass[v];[1:a]atrim=0:DUR,afade=t=out:st=DUR-0.5:d=0.5,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
 -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -movflags +faststart -shortest final.mp4
```
نموذج `caption.ass`:
```
[Script Info]
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Alignment, MarginL, MarginR, MarginV, BorderStyle, Outline, Shadow
Style: Cap,Cairo,82,&H00FFFFFF,&H00000000,&H80000000,0,8,120,120,290,1,1.5,1
[Events]
Format: Layer, Start, End, Style, Text
Dialogue: 0,0:00:00.00,0:00:59.00,Cap,أنا لما أكون متأخر على الشغل\N77 دقيقة وأنا سايق\Nتسلا رودستر
```
- قواعد النص: 3 أسطر كحد أقصى، 8–14 كلمة، يبدأ بـ "Me when / أنا لما"، فيه رقم محدد غريب، ينتهي باسم المنتج/الحالة.

### و. الصوت
- الافتراضي: موسيقى المستخدم أو ترند، مع إزالة الصوت الأصلي (أو خفضه إلى −25dB كخلفية).
- طابق: أول ضربة قوية ← الإقلاع، الضربة التالية الكبيرة ← كشف المدينة.
- الجهارة النهائية −14 LUFS، قمة −1.5dBTP.

---

## 4) قائمة فحص الجودة قبل التسليم
- [ ] الشخص نفسه 100% (وجه، يدين، ملابس) في الجزء المولّد — قارن فريمات جنباً لجنب.
- [ ] لا يوجد ذوبان أو تشوه في المقود/الشاشة/المقاعد.
- [ ] الانتقال غير مرئي: المشاهد يرى "وهج شمس" وليس قطعاً.
- [ ] الكابشن ثابت، مقروء على الخلفية الفاتحة (أضف ظل/حدّ إن لزم)، لا يغطي الوجه، داخل المنطقة الآمنة.
- [ ] 1080×1920، 30fps، 10–15ث، الصوت لا يتقطع، ينتهي عند ذروة الطيران.
- [ ] استخرج 3 فريمات (بداية / إقلاع / مدينة) وأرسلها للمستخدم للمعاينة مع الملف النهائي.
