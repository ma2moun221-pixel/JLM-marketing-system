# وصفات ffmpeg

عمليات خارج `render.py` — تحضير المصدر، تشخيص، وحالات خاصة.
كلها بأدوات مجانية. **لا تُستخدم `drawtext` لنص عربي أبدًا** (يقطّع الحروف ويعكس الاتجاه).

## تحضير المصدر

```bash
# تصحيح الدوران المضمّن في الميتاداتا (فيديو الجوال المقلوب)
ffmpeg -i in.mp4 -vf "transpose=1" -c:a copy fixed.mp4      # 90° يمين
ffmpeg -i in.mp4 -vf "transpose=2" -c:a copy fixed.mp4      # 90° يسار
ffmpeg -i in.mp4 -vf "transpose=1,transpose=1" -c:a copy fixed.mp4  # 180°

# دمج عدة مقاطع (يتطلّب نفس الترميز والأبعاد)
printf "file 'a.mp4'\nfile 'b.mp4'\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4

# دمج مقاطع مختلفة الترميز/الأبعاد — يعيد الترميز
ffmpeg -i a.mp4 -i b.mp4 -filter_complex \
 "[0:v]scale=1080:1920,setsar=1[v0];[1:v]scale=1080:1920,setsar=1[v1];\
  [v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" \
 -map "[v]" -map "[a]" -crf 18 -preset medium -pix_fmt yuv420p joined.mp4

# استخراج مقطع بلا إعادة ترميز (يقصّ عند أقرب إطار مفتاحي)
ffmpeg -ss 12.5 -i in.mp4 -t 20 -c copy clip.mp4

# قصّ دقيق بالإطار (يعيد الترميز)
ffmpeg -i in.mp4 -ss 12.5 -t 20 -crf 18 -preset medium -pix_fmt yuv420p clip.mp4
```

## الأبعاد

```bash
# أفقي → عمودي بخلفية ضبابية (الطريقة المستخدمة في render.py)
ffmpeg -i in.mp4 -filter_complex \
 "[0:v]split=2[bg][fg];\
  [bg]scale=136:-2,gblur=sigma=6,scale=1080:1920:force_original_aspect_ratio=increase,\
      crop=1080:1920,eq=brightness=-0.10:saturation=0.85[bgb];\
  [fg]scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos[fgs];\
  [bgb][fgs]overlay=(W-w)/2:(H-h)/2[v]" \
 -map "[v]" -map 0:a -crf 18 -preset medium -pix_fmt yuv420p out.mp4
```

التمويه على نسخة مصغّرة ثم التكبير: نفس المظهر بكلفة أقل بعشرات المرات من
`gblur` بسيغما كبيرة على الإطار الكامل.

```bash
# قصّ مركزي إلى 9:16
ffmpeg -i in.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
 -crf 18 -preset medium -pix_fmt yuv420p out.mp4

# قصّ من موضع مخصّص (الشخص ليس في المنتصف)
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih:(iw-ih*9/16)*0.30:0,scale=1080:1920" \
 -crf 18 -preset medium -pix_fmt yuv420p out.mp4
```

`0.30` نسبة موضع القصّ أفقيًا: `0` أقصى اليسار، `1` أقصى اليمين.

## الصوت

```bash
# تطبيع إلى -14 LUFS (تمريرتان = أدقّ من تمريرة واحدة)
ffmpeg -i in.mp4 -af "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null -
# انسخ measured_* من المخرج إلى:
ffmpeg -i in.mp4 -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=…:measured_TP=…:\
measured_LRA=…:measured_thresh=…:linear=true" -c:v copy out.mp4

# موسيقى مع خفض تلقائي وقت الكلام (ducking)
ffmpeg -i video.mp4 -i music.mp3 -filter_complex \
 "[0:a]highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11,asplit=2[sp][key];\
  [1:a]volume=-18dB,aloop=loop=-1:size=2e9[mus];\
  [mus][key]sidechaincompress=threshold=0.02:ratio=12:attack=15:release=350[duck];\
  [sp][duck]amix=inputs=2:duration=first,alimiter=limit=0.95[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k out.mp4

# تقليل ضجيج خلفية ثابت
ffmpeg -i in.mp4 -af "afftdn=nf=-25" -c:v copy out.mp4

# استخراج الصوت للتفريغ
ffmpeg -i in.mp4 -vn -ar 16000 -ac 1 -c:a pcm_s16le audio.wav
```

## النص والكابشن

```bash
# حرق كابشن ASS (الطريقة الصحيحة للعربية)
ffmpeg -i in.mp4 -vf "ass=captions.ass" -crf 18 -preset medium -c:a copy out.mp4

# مع مجلد خطوط مخصّص
ffmpeg -i in.mp4 -vf "ass=captions.ass:fontsdir=/path/to/fonts" -crf 18 -c:a copy out.mp4

# من SRT بنمط مخصّص (لاتيني فقط — للعربية استخدم ASS)
ffmpeg -i in.mp4 -vf "subtitles=in.srt:force_style='FontName=Cairo,FontSize=24,\
Outline=3,Alignment=2'" -crf 18 -c:a copy out.mp4
```

## طبقات وأيقونات

```bash
# شعار ثابت شفّاف
ffmpeg -i in.mp4 -i logo.png -filter_complex \
 "[1:v]scale=160:-1[lg];[0:v][lg]overlay=W-w-40:40" -crf 18 -c:a copy out.mp4

# أيقونة تظهر وتختفي بتوقيت
ffmpeg -i in.mp4 -i icon.png -filter_complex \
 "[1:v]scale=180:180[ic];[0:v][ic]overlay=W*0.8:H*0.15:enable='between(t,3,6)'" \
 -crf 18 -c:a copy out.mp4

# شريط تقدّم أسفل الشاشة (يرفع نسبة إكمال المشاهدة)
ffmpeg -i in.mp4 -vf \
 "drawbox=x=0:y=ih-12:w='iw*t/DURATION':h=12:color=yellow@0.9:t=fill" \
 -crf 18 -c:a copy out.mp4
```

استبدل `DURATION` بمدة الفيديو بالثواني.

⚠️ **صورة ثابتة كطبقة متحرّكة**: يجب تكرارها وإعطاؤها توقيتات، وإلا بقي `t=0` ولم تتحرّك:

```
[1:v]format=rgba,loop=loop=-1:size=1:start=0,fps=30,setpts=N/30/TB,scale=…:eval=frame
```

## اللون

```bash
# تدرّج خفيف آمن للبشرة
ffmpeg -i in.mp4 -vf "eq=contrast=1.08:saturation=1.10:brightness=0.02" \
 -crf 18 -c:a copy out.mp4

# مع زيادة حدّة للقطات الهاتف الناعمة
ffmpeg -i in.mp4 -vf "eq=contrast=1.08:saturation=1.10,unsharp=5:5:0.6:5:5:0.0" \
 -crf 18 -c:a copy out.mp4

# تطبيق LUT مجاني (.cube)
ffmpeg -i in.mp4 -vf "lut3d=file=grade.cube" -crf 18 -c:a copy out.mp4
```

## الحركة

```bash
# تسريع 1.1× (صوت وصورة معًا)
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=PTS/1.1[v];[0:a]atempo=1.1[a]" \
 -map "[v]" -map "[a]" -crf 18 -preset medium out.mp4

# سلو موشن 0.5× (يحتاج مصدر 60fps فأعلى ليبقى ناعمًا)
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=PTS*2[v];[0:a]atempo=0.5[a]" \
 -map "[v]" -map "[a]" -crf 18 out.mp4

# تكبير بطيء (ken burns)
ffmpeg -i in.mp4 -vf "zoompan=z='min(zoom+0.0012,1.15)':d=1:\
x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30" \
 -crf 18 -c:a copy out.mp4

# انتقال تلاشٍ بين مقطعين
ffmpeg -i a.mp4 -i b.mp4 -filter_complex \
 "[0:v][1:v]xfade=transition=fade:duration=0.4:offset=4.6[v]" \
 -map "[v]" -crf 18 out.mp4
```

`atempo` يقبل `0.5–2.0` لكل نسخة — سلسِل عدة نسخ للسرعات خارج المدى:
`atempo=2.0,atempo=1.5` = 3×.

## تشخيص

```bash
ffprobe -v error -show_format -show_streams -of json in.mp4   # كل شيء
ffmpeg -i in.mp4 -af silencedetect=noise=-32dB:d=0.35 -f null -   # فترات الصمت
ffmpeg -i in.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null -  # تغيّر المشهد
ffmpeg -i in.mp4 -af "loudnorm=I=-14:print_format=json" -f null - # قياس الصوت
ffmpeg -ss 5 -i in.mp4 -frames:v 1 frame.png                      # لقطة للمراجعة
ffmpeg -i in.mp4 -vf "fps=1/3,scale=320:-1,tile=4x3" contact.png   # ورقة تعريف
```

`probe.py` يغلّف أول أربعة منها ويترجم الأرقام إلى قرارات مونتاج.
