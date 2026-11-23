# مكتبة ستايلات المونتاج (17 ستايلًا) وربطها بأنواع المحتوى

> **المصدر:** فيديو Reel مدته 33 ثانية لصانع المحتوى Ram Ramez، أرسله مأمون حجاوي في 2026-11-23.
> **الحالة:** أسماء الستايلات الـ 17 وترتيبها منقولة حرفيًا من قائمة التحقق الظاهرة على الشاشة (**FACT**)، ووصف «ما يظهر» مأخوذ من إطارات الفيديو. طريقة التنفيذ والفائدة والربط بأنواع المحتوى والشروط هي تحليلنا (**INSIGHT / RECOMMENDATION**).
> **مصدر الحقيقة في الكود:** `src/lib/ai/system-prompt/edit-styles.ts`، وهذا الملف مولَّد منه.
> **ملاحظة:** الصوت لم يُفرَّغ آليًا (أداة التفريغ غير متاحة في بيئة التحليل)؛ التحليل مبني على الصورة والنصوص الظاهرة.

## تحليل الفيديو نفسه

**الفكرة:** المتحدث يطلب من Claude بالعامية المصرية «اعملي الـ edits دي»، ثم يمر على 17 ستايل مونتاج، ستايل واحد كل ثانيتين تقريبًا، على لقطة واحدة له جالسًا على كرسي في شرفة.

**البنية:**
1. **الخطاف (0–1.5 ث):** جملة قصيرة على الشاشة تعد بشيء محدد (17 edit) + أول ستايل (Orbit) فورًا بدون مقدمة.
2. **الجسم (1.5–31 ث):** ستايل جديد كل ~2 ثانية، وكل ستايل يحمل اسمه بخط Serif برتقالي أسفل الشاشة.
3. **الختام (31–33 ث):** Glass type بكلمة «EDITS» ثم اكتمال القائمة 17/17.

**عناصر ثابتة طوال الفيديو (سر قوته):**
- **قائمة تحقق جانبية** على اليسار بكل الستايلات، تتعبأ بعلامة ✓ مع كل ستايل، فيعرف المشاهد كم بقي ويبقى للنهاية (Open loop).
- **عداد** أعلى اليمين (01/17 … 17/17) يعطي إحساس التقدم.
- **هوية بصرية موحدة:** لون برتقالي واحد + خط Serif واحد في كل العناصر.
- **لقطة خام واحدة** بدون تغيير مكان، والمونتاج وحده يصنع التنوع؛ تكلفة تصوير منخفضة جدًا.

**تصنيفه حسب مكتبة أنواع المحتوى:** MOFU · **Educational / How to** بأسلوب **Founder led**، ومعه قابلية انتشار عالية لأنه قائمة (Listicle) يحفظها الناس ويرسلونها.

**الدرس لـ JLM (INSIGHT):** لقطة واحدة لميكانيكي أو لمدير JLM في الكراج، مع 4–6 ستايلات مونتاج وقائمة تحقق وعداد، تكفي لصنع فيديو تعليمي يبدو احترافيًا بدون تصوير معقد.

## الجدول المختصر

| # | الستايل | بالعربي | التوقيت | الصعوبة | الأنسب لـ |
|---|---|---|---|---|---|
| 1 | Orbit | مدار حول الرأس | 00:01–00:03 | متقدم | Founder led، Educational، Expert Explainer، How to، Event announcement |
| 2 | Couch wall | جدار المحتوى خلف المتحدث | 00:03–00:05 | متوسط | Social proof Collage، Case Studies، Behind the scene، Founder led، UGC testimonials |
| 3 | UI world | عالم الواجهة | 00:05–00:07 | متوسط | How to، Educational، Check out mockup، Behind the scene |
| 4 | Frame break | كسر الإطار | 00:07–00:09 | متوسط | Before and after، Product Image، Studio Shoots، Founder led، Celebrity |
| 5 | Digital zoom | زوم رقمي (Punch-in) | 00:09–00:10 | سهل | Educational، Expert Explainer، FAQs، Comment Response، Founder led، Podcast، Memes |
| 6 | Full mockup | موك-أب هاتف كامل | 00:10–00:12 | سهل | Check out mockup، Phone call Mockup، Comment Response، UGC testimonials، News mockup، Social proof Collage |
| 7 | Checklist | قائمة تحقق | 00:12–00:14 | سهل | How to، FAQs، Educational، Freebies، Offer first banners |
| 8 | Headline wall | جدار العناوين والأرقام | 00:14–00:16 | سهل | Text Heavy statics، Case Studies، Price comparison، Certification Badges، Billboard، News mockup |
| 9 | Zoom through cut | قطع بالزوم العابر | 00:16–00:18 | سهل | Memes، Before and after، Founder led، Countdown، FOMO offers |
| 10 | Chart grow | رسم بياني ينمو | 00:18–00:20 | متوسط | Case Studies، Price comparison، Educational، Before and after |
| 11 | Pull back reveal | الكشف بالابتعاد | 00:20–00:22 | متوسط | Behind the scene، Check out mockup، How to، Case Studies |
| 12 | Green screen | استبدال الخلفية | 00:22–00:24 | سهل | Comment Response، News mockup، Studio Shoots، Expert Explainer، Celebrity |
| 13 | Paper cut | قص ورقي (كولاج) | 00:24–00:25 | متوسط | Memes، Educational، FAQs، Event announcement، Freebies |
| 14 | Doodle boil | رسومات يدوية متحركة | 00:26–00:27 | متوسط | Memes، Founder led، Comment Response، Before and after، Freebies |
| 15 | Vertigo | دولي زوم (Vertigo) | 00:27–00:29 | متقدم | News mockup، Before and after، Countdown، FOMO offers، Founder led |
| 16 | Cover story | غلاف مجلة | 00:29–00:31 | متوسط | Founder led، Celebrity، Event announcement، Case Studies، Studio Shoots |
| 17 | Glass type | نص زجاجي | 00:31–00:33 | متوسط | Product Image، Studio Shoots، Billboard، Text Heavy statics، Offer first banners |

## قواعد استخدام الستايلات في أي فيديو (RECOMMENDATION)

1. **لكل فيديو 2–4 ستايلات**، وليس 17. فيديو Ram Ramez استعرض الستايلات كمحتوى بحد ذاته؛ في فيديو JLM العادي يجب أن يخدم الستايل الرسالة.
2. **الخطاف (0–3 ث):** Orbit، Zoom through cut، Vertigo، Frame break، Doodle boil.
3. **الوسط (الشرح والإثبات):** Checklist، Headline wall، Chart grow، Full mockup، UI world، Digital zoom.
4. **الختام (تثبيت الرسالة أو المنتج):** Glass type، Cover story، Pull back reveal.
5. **Digital zoom** كل 3–5 ثوانٍ في أي Talking head لكسر الرتابة.
6. **ستايل متقدم واحد كحد أقصى** في الفيديو القصير (Orbit أو Vertigo).
7. **هوية JLM:** لون العلامة في النصوص والبطاقات، خط واحد ثابت، وصورة المنتج الحقيقية دون أي تعديل على العبوة أو الشعار.
8. **الستايلات التي تعرض أرقامًا أو رسائل عملاء** (Headline wall، Chart grow، Couch wall، Full mockup) تحتاج بيانات حقيقية من قاعدة المعرفة.

## الستايلات المقترحة لكل نوع من أنواع المحتوى الـ 28

| نوع المحتوى | المرحلة | ستايلات المونتاج المقترحة |
|---|---|---|
| Before and after (قبل وبعد) | TOFU | Frame break، Zoom through cut، Chart grow، Doodle boil، Vertigo |
| Behind the scene (خلف الكواليس) | TOFU | Couch wall، UI world، Pull back reveal |
| Memes (ميمز) | TOFU | Digital zoom، Zoom through cut، Paper cut، Doodle boil |
| Celebrity (مشاهير / مؤثرون) | TOFU | Frame break، Green screen، Cover story |
| Billboard (لوحة إعلانية (Billboard)) | TOFU | Headline wall، Glass type |
| Event announcement (إعلان فعالية) | TOFU | Orbit، Paper cut، Cover story |
| Founder led (محتوى يقوده المؤسس/المدير) | TOFU | Orbit، Couch wall، Frame break، Digital zoom، Zoom through cut، Doodle boil، Vertigo، Cover story |
| Phone call Mockup (موك-أب مكالمة هاتفية) | TOFU | Full mockup |
| News mockup (موك-أب خبر عاجل) | TOFU | Full mockup، Headline wall، Green screen، Vertigo |
| Comment Response (الرد على تعليق) | MOFU | Digital zoom، Full mockup، Green screen، Doodle boil |
| Case Studies (دراسات حالة) | MOFU | Couch wall، Headline wall، Chart grow، Pull back reveal، Cover story |
| Certification Badges (شارات الاعتماد والشهادات) | MOFU | Headline wall |
| Educational (تعليمي) | MOFU | Orbit، UI world، Digital zoom، Checklist، Chart grow، Paper cut |
| Expert Explainer (شرح خبير) | MOFU | Orbit، Digital zoom، Green screen |
| FAQs (أسئلة شائعة) | MOFU | Digital zoom، Checklist، Paper cut |
| How to (طريقة الاستخدام (How to)) | MOFU | Orbit، UI world، Checklist، Pull back reveal |
| Podcast (بودكاست / مقطع حواري) | MOFU | Digital zoom |
| Social proof Collage (مجمّع الدليل الاجتماعي) | MOFU | Couch wall، Full mockup |
| Text Heavy statics (تصاميم نصية ثابتة) | MOFU | Headline wall، Glass type |
| Check out mockup (موك-أب صفحة الدفع/الطلب) | BOFU | UI world، Full mockup، Pull back reveal |
| Countdown (عد تنازلي) | BOFU | Zoom through cut، Vertigo |
| Offer first banners (بانر العرض أولًا) | BOFU | Checklist، Glass type |
| Product Image (صورة المنتج) | BOFU | Frame break، Glass type |
| Studio Shoots (تصوير استوديو) | BOFU | Frame break، Green screen، Cover story، Glass type |
| UGC testimonials (شهادات العملاء (UGC)) | BOFU | Couch wall، Full mockup |
| Price comparison (مقارنة السعر/القيمة) | BOFU | Headline wall، Chart grow |
| FOMO offers (عروض الخوف من الفوات (FOMO)) | BOFU | Zoom through cut، Vertigo |
| Freebies (هدايا ومجاني مع الطلب) | BOFU | Checklist، Paper cut، Doodle boil |

## أمثلة تطبيقية لفيديوهات JLM (RECOMMENDATION، أفكار للتنفيذ وليست منشورة)

### 1. فيديو هادف: «3 علامات إنه بخاخات سيارتك بدها تنظيف» (MOFU · Educational)
| الوقت | الستايل | ماذا يظهر |
|---|---|---|
| 0–2 ث | Orbit | 3 بطاقات (دخان، رجفة، استهلاك) تدور حول رأس الميكانيكي |
| 2–12 ث | Checklist + Digital zoom | كل علامة تتعبأ ✓ مع زوم على الوجه عند كل واحدة |
| 12–18 ث | Full mockup | هاتف يعرض طريقة الطلب عبر واتساب |
| 18–20 ث | Glass type | اسم المنتج بنص زجاجي خلف الميكانيكي |

### 2. فيديو Viral: «لما الزبون يقول للميكانيكي: في صوت غريب» (TOFU · Memes)
| الوقت | الستايل | ماذا يظهر |
|---|---|---|
| 0–1 ث | Zoom through cut | تقريب على وجه الميكانيكي المصدوم |
| 1–5 ث | Doodle boil | علامات استفهام ونجوم مرسومة تهتز حول رأسه |
| 5–8 ث | Vertigo | لحظة «اكتشاف» سبب الصوت |
| 8–10 ث | Paper cut | الختام بمظهر ملصق مرح واسم JLM |

### 3. فيديو بيعي: «نفس المشكلة… فاتورة مختلفة» (BOFU · Price comparison)
| الوقت | الستايل | ماذا يظهر |
|---|---|---|
| 0–2 ث | Frame break | المتحدث يخرج من إطار فاتورة إصلاح |
| 2–8 ث | Headline wall | تكلفة الإصلاح مقابل سعر العبوة (أرقام موثقة ومؤرخة فقط) |
| 8–12 ث | Full mockup | محادثة الطلب على واتساب |
| 12–14 ث | Glass type | اسم المنتج |

## أين يستخدم النظام هذه المكتبة

- **كل أوضاع الذكاء الاصطناعي** تستلم المكتبة ضمن البرومبت الثابت.
- **Reel / TikTok / Monthly Plan / Purposeful / Viral:** كل فيديو يخرج مع خطة مونتاج (2–4 ستايلات وتوقيتها).
- **Edit Director Mode (جديد):** الصق أي فيديو أو سكربت، فيقترح نوع المحتوى وجدول المونتاج ليصبح أجمل وأقوى.
- **قالب برومبت جديد:** «اقتراح أنواع وستايلات مونتاج لفيديو».

## التفاصيل الكاملة لكل ستايل

### 1. Orbit — مدار حول الرأس

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:01–00:03) | بطاقات صغيرة (Cut، Grade، Captions، Effects) تدور حول رأس المتحدث في مسار ثلاثي الأبعاد، بعضها أمامه وبعضها خلفه. |
| طريقة التنفيذ | عزل المتحدث (Remove background / Rotoscope) ووضعه بطبقة فوق البطاقات الخلفية وتحت الأمامية؛ تحريك البطاقات بـ Keyframes على مسار بيضاوي. |
| الفائدة | خطاف بصري في أول 3 ثوانٍ يعرض مكونات الفكرة كلها مرة واحدة. |
| الصعوبة | متقدم |
| الأنسب لأنواع المحتوى | Founder led، Educational، Expert Explainer، How to، Event announcement |
| الشرط | — |

### 2. Couch wall — جدار المحتوى خلف المتحدث

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:03–00:05) | خلفية المتحدث تتحول إلى جدار من صور مصغّرة لمنشورات/ريلز سابقة بينما يبقى هو في المقدمة. |
| طريقة التنفيذ | عزل المتحدث + شبكة صور (Grid) خلفه مع حركة بطيئة أو ظهور متتابع للصور. |
| الفائدة | إثبات حجم العمل أو الانتشار بلقطة واحدة؛ «انظر كم عملنا». |
| الصعوبة | متوسط |
| الأنسب لأنواع المحتوى | Social proof Collage، Case Studies، Behind the scene، Founder led، UGC testimonials |
| الشرط | الصور في الجدار حقيقية (منشورات أو شهادات فعلية) لا لقطات مؤلفة. |

### 3. UI world — عالم الواجهة

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:05–00:07) | نافذة برنامج/Terminal تظهر خلف المتحدث وتكتب أوامر («edit my reel») ثم تعرض التقدم. |
| طريقة التنفيذ | تصميم واجهة (لقطة شاشة أو Mockup) خلف المتحدث المعزول مع كتابة نص متحركة (Typewriter). |
| الفائدة | يشرح عملية أو أداة كأن المشاهد يراها من الداخل. |
| الصعوبة | متوسط |
| الأنسب لأنواع المحتوى | How to، Educational، Check out mockup، Behind the scene |
| الشرط | — |

### 4. Frame break — كسر الإطار

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:07–00:09) | الفيديو يصغر داخل إطار بحواف دائرية على خلفية داكنة، والمتحدث يبرز خارج حدود الإطار. |
| طريقة التنفيذ | تصغير اللقطة داخل إطار + نسخة معزولة من المتحدث فوق الإطار بحيث يتجاوز رأسه/جسمه الحافة. |
| الفائدة | عمق ثلاثي الأبعاد يلفت العين؛ يصلح لتمييز لحظة مهمة. |
| الصعوبة | متوسط |
| الأنسب لأنواع المحتوى | Before and after، Product Image، Studio Shoots، Founder led، Celebrity |
| الشرط | — |

### 5. Digital zoom — زوم رقمي (Punch-in)

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:09–00:10) | قفزة تقريب مفاجئة على الوجه من نفس اللقطة. |
| طريقة التنفيذ | Scale من 100% إلى 130–150% على قطع (Cut) أو بانتقال سريع؛ التصوير بدقة 4K يحافظ على الجودة. |
| الفائدة | أبسط طريقة لكسر الرتابة والتأكيد على جملة مهمة. |
| الصعوبة | سهل |
| الأنسب لأنواع المحتوى | Educational، Expert Explainer، FAQs، Comment Response، Founder led، Podcast، Memes |
| الشرط | — |

### 6. Full mockup — موك-أب هاتف كامل

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:10–00:12) | هاتف ينزلق من طرف الشاشة ويعرض ريل/تطبيقًا بجانب المتحدث. |
| طريقة التنفيذ | إطار هاتف PNG + تسجيل شاشة داخله، يدخل بحركة Slide مع Ease. |
| الفائدة | يعرض منشورًا، رسالة، أو تجربة طلب داخل سياق الهاتف المألوف. |
| الصعوبة | سهل |
| الأنسب لأنواع المحتوى | Check out mockup، Phone call Mockup، Comment Response، UGC testimonials، News mockup، Social proof Collage |
| الشرط | ما يظهر داخل الهاتف حقيقي (رسالة/تعليق/صفحة طلب فعلية) أو موضح أنه تمثيل. |

### 7. Checklist — قائمة تحقق

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:12–00:14) | بطاقة بمربعات تتعبأ بعلامة ✓ واحدًا تلو الآخر («Cut the pauses، Add captions، Add 17 edits»). |
| طريقة التنفيذ | عناصر نص + مربعات تظهر بالتتابع مع صوت «تك» عند كل علامة. |
| الفائدة | يحول الخطوات أو الفوائد إلى تقدم مرئي مُرضٍ؛ سهل الحفظ. |
| الصعوبة | سهل |
| الأنسب لأنواع المحتوى | How to، FAQs، Educational، Freebies، Offer first banners |
| الشرط | — |

### 8. Headline wall — جدار العناوين والأرقام

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:14–00:16) | أرقام وعبارات ضخمة تظهر متتابعة بجانب المتحدث: «17 edits / 0 editors / 1 prompt». |
| طريقة التنفيذ | Kinetic typography: أرقام كبيرة بلون العلامة تظهر بـ Pop أو Slide على إيقاع الكلام. |
| الفائدة | يرسخ الرسالة في أرقام قليلة يتذكرها المشاهد. |
| الصعوبة | سهل |
| الأنسب لأنواع المحتوى | Text Heavy statics، Case Studies، Price comparison، Certification Badges، Billboard، News mockup |
| الشرط | كل رقم يظهر يجب أن يكون موثقًا في قاعدة المعرفة. |

### 9. Zoom through cut — قطع بالزوم العابر

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:16–00:18) | تقريب شديد جدًا حتى يملأ الوجه الشاشة ثم قطع إلى لقطة واسعة. |
| طريقة التنفيذ | Zoom in سريع مع Motion blur على آخر فريمات المقطع، ثم Cut للقطة التالية (أو Zoom out منها). |
| الفائدة | انتقال بطاقة عالية يربط فكرتين ويمنع الملل. |
| الصعوبة | سهل |
| الأنسب لأنواع المحتوى | Memes، Before and after، Founder led، Countdown، FOMO offers |
| الشرط | — |

### 10. Chart grow — رسم بياني ينمو

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:18–00:20) | خط رسم بياني برتقالي يصعد خلف المتحدث بعنوان «views» وينتهي بـ «+840%». |
| طريقة التنفيذ | خط بياني (Shape layer أو Trim path) يُرسم تدريجيًا مع عداد رقم يرتفع. |
| الفائدة | يجعل النتيجة أو التحسن ملموسًا ومقنعًا. |
| الصعوبة | متوسط |
| الأنسب لأنواع المحتوى | Case Studies، Price comparison، Educational، Before and after |
| الشرط | البيانات حقيقية ومقاسة فقط؛ لا رسوم بيانية توضيحية تبدو كنتائج. |

### 11. Pull back reveal — الكشف بالابتعاد

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:20–00:22) | الكاميرا «تبتعد» فيتضح أن الفيديو يُعرض داخل واجهة برنامج مونتاج مع شريط زمني وحالة «17/17 edits applied». |
| طريقة التنفيذ | Scale down للفيديو داخل تصميم واجهة/شاشة/هاتف أكبر، مع حركة سلسة. |
| الفائدة | لحظة مفاجأة تكشف «الكواليس» أو السياق الحقيقي. |
| الصعوبة | متوسط |
| الأنسب لأنواع المحتوى | Behind the scene، Check out mockup، How to، Case Studies |
| الشرط | — |

### 12. Green screen — استبدال الخلفية

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:22–00:24) | خلفية الشرفة تتحول إلى استوديو أبيض نظيف والمتحدث كما هو. |
| طريقة التنفيذ | Remove background (CapCut/Premiere) أو كروما حقيقية، ثم وضع خلفية جديدة مع ظل خفيف. |
| الفائدة | ينقل المتحدث إلى أي مكان: كراج، محل قطع، صورة المنتج، أو خبر. |
| الصعوبة | سهل |
| الأنسب لأنواع المحتوى | Comment Response، News mockup، Studio Shoots، Expert Explainer، Celebrity |
| الشرط | لا خلفيات توحي بمكان أو حدث لم يحصل (مثلًا معرض لم نشارك فيه). |

### 13. Paper cut — قص ورقي (كولاج)

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:24–00:25) | المتحدث بحدود بيضاء كالملصق فوق خلفية أشكال ورقية ملونة (برتقالي، كريمي، أزرق). |
| طريقة التنفيذ | عزل المتحدث + Stroke أبيض سميك + خلفية كولاج أشكال مسطحة. |
| الفائدة | مظهر يدوي مرح يميز المحتوى عن الإعلانات التقليدية. |
| الصعوبة | متوسط |
| الأنسب لأنواع المحتوى | Memes، Educational، FAQs، Event announcement، Freebies |
| الشرط | — |

### 14. Doodle boil — رسومات يدوية متحركة

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:26–00:27) | رسومات بيضاء مرسومة باليد (تاج، نجوم، خطوط متموجة) تهتز حول رأس المتحدث. |
| طريقة التنفيذ | رسومات بخط يدوي بـ 2–3 نسخ مختلفة قليلًا تتبدل كل 2–3 فريمات (Boil effect). |
| الفائدة | يضيف شخصية وفكاهة ويوجه العين لنقطة معينة. |
| الصعوبة | متوسط |
| الأنسب لأنواع المحتوى | Memes، Founder led، Comment Response، Before and after، Freebies |
| الشرط | — |

### 15. Vertigo — دولي زوم (Vertigo)

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:27–00:29) | المتحدث ثابت الحجم بينما الخلفية تتمدد وتبتعد، إحساس دوار سينمائي. |
| طريقة التنفيذ | أثناء التصوير: تحريك الكاميرا للخلف مع تقريب العدسة. في المونتاج: عزل المتحدث وتكبير الخلفية بعكس اتجاهه. |
| الفائدة | لحظة درامية لكشف مفاجأة أو مشكلة. |
| الصعوبة | متقدم |
| الأنسب لأنواع المحتوى | News mockup، Before and after، Countdown، FOMO offers، Founder led |
| الشرط | — |

### 16. Cover story — غلاف مجلة

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:29–00:31) | تصميم غلاف مجلة: اسم ضخم خلف الرأس، سطر «The edits issue · Nov 2026» وعبارة «No editor needed.». |
| طريقة التنفيذ | عزل المتحدث + Masthead بخط Serif كبير خلفه + عناوين صغيرة كغلاف مجلة. |
| الفائدة | يعطي قيمة ومكانة؛ ممتاز لإعلان أو قصة شخصية. |
| الصعوبة | متوسط |
| الأنسب لأنواع المحتوى | Founder led، Celebrity، Event announcement، Case Studies، Studio Shoots |
| الشرط | لا تقليد لاسم أو شعار مجلة حقيقية. |

### 17. Glass type — نص زجاجي

| البند | التفاصيل |
|---|---|
| ما يظهر في الفيديو (00:31–00:33) | كلمة ضخمة «EDITS» بتأثير زجاج شفاف ضبابي خلف المتحدث. |
| طريقة التنفيذ | نص كبير مع Blur للخلفية خلفه + حدود فاتحة (Glassmorphism)، والمتحدث المعزول أمامه. |
| الفائدة | ختام أنيق يثبت الكلمة المفتاحية أو اسم المنتج. |
| الصعوبة | متوسط |
| الأنسب لأنواع المحتوى | Product Image، Studio Shoots، Billboard، Text Heavy statics، Offer first banners |
| الشرط | — |
