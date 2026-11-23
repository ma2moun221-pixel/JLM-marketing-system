/**
 * Content-type library: 28 ad/content formats mapped to the funnel stage
 * (TOFU / MOFU / BOFU) where each one does its job.
 *
 * Source: a 28-second Instagram Reel by @adsandcopy supplied by the owner
 * (analysed 2026-11-23). The 28 type names and their funnel stage are taken
 * verbatim from the video's on-screen list (FACT). Definitions, purposes,
 * formats, hooks, CTAs, JLM applications and guardrails are our own
 * analysis (INSIGHT / RECOMMENDATION). Full write-up:
 * docs/content-types/content-types-funnel.md
 *
 * This is the single source of truth: the prompt block below is generated
 * from CONTENT_TYPES, so editing an entry updates every AI mode at once.
 * Static on every request, so compose.ts sends it as a cached block.
 */

export type FunnelStage = "TOFU" | "MOFU" | "BOFU";

export type ContentType = {
  key: string;
  nameEn: string;
  nameAr: string;
  stage: FunnelStage;
  /** What it is. */
  definition: string;
  /** The job it does in the funnel. */
  purpose: string;
  /** Formats it works best in. */
  formats: string;
  /** The example shown in the source video (observation only). */
  videoExample: string;
  /** How JLM can use it. */
  jlmUse: string;
  /** Hook pattern (Palestinian Arabic). */
  hook: string;
  cta: string;
  /** Can it carry purposeful (value-first) content? */
  purposeful: boolean;
  /** Does it have high share/viral potential? */
  viral: boolean;
  /** Evidence rule that must hold before this type is used. */
  guardrail?: string;
};

export const FUNNEL_STAGES: Record<FunnelStage, { ar: string; goal: string; kpi: string }> = {
  TOFU: {
    ar: "أعلى القمع — الوعي",
    goal: "لفت انتباه ناس ما بتعرف JLM أو ما بتعرف إنها عندها مشكلة؛ الوصول والتذكر.",
    kpi: "Reach، Views، نسبة المشاهدة 3 ثوانٍ، Shares، Saves، متابعين جدد.",
  },
  MOFU: {
    ar: "منتصف القمع — الاعتبار والثقة",
    goal: "تحويل المهتم إلى مقتنع: تعليم، إجابة اعتراضات، إثبات، خبرة.",
    kpi: "مدة المشاهدة، Saves، تعليقات وأسئلة، زيارات صفحة المنتج، رسائل استفسار.",
  },
  BOFU: {
    ar: "أسفل القمع — القرار والشراء",
    goal: "دفع الجاهز للشراء لاتخاذ القرار الآن: عرض، دليل نهائي، إلحاح، سهولة الطلب.",
    kpi: "رسائل واتساب/ماسنجر للطلب، نقرات الشراء، المبيعات، تكلفة الطلب، استخدام كود العرض.",
  },
};

export const CONTENT_TYPES: ContentType[] = [
  // ───────────── TOFU — الوعي ─────────────
  {
    key: "before-after",
    nameEn: "Before and after",
    nameAr: "قبل وبعد",
    stage: "TOFU",
    definition: "مقارنة بصرية بين حالة المشكلة وحالة النتيجة في نفس الكادر أو بالتتابع.",
    purpose: "يوقف التمرير فورًا لأن العين تبحث عن الفرق؛ يشرح قيمة المنتج بدون كلام.",
    formats: "Reel انتقال (Transition)، صورة مقسومة، كاروسيل شريحتين.",
    videoExample: "بوستر عناية بالبشرة: Before (جفاف وملمس غير متساوٍ) / After (بشرة ناعمة).",
    jlmUse: "دخان العادم، صوت المحرك، نظافة البخاخات أو غرفة الاحتراق قبل وبعد استخدام منتج — مصوّر فعليًا في كراج.",
    hook: "«شوف الفرق… نفس السيارة، بس بعد 300 كم»",
    cta: "احفظ الفيديو / ابعته لصاحبك اللي سيارته بتدخّن",
    purposeful: true,
    viral: true,
    guardrail: "تصوير حقيقي فقط بنفس الإضاءة والزاوية؛ لا تعديل ولا توليد بالذكاء الاصطناعي؛ لا أرقام نتائج غير موثقة.",
  },
  {
    key: "behind-the-scenes",
    nameEn: "Behind the scene",
    nameAr: "خلف الكواليس",
    stage: "TOFU",
    definition: "لقطات من داخل الشغل الحقيقي: المستودع، التغليف، تصوير المحتوى، زيارات الكراجات.",
    purpose: "يؤنسن العلامة ويبني ألفة؛ محتوى سهل الإنتاج ويبدو صادقًا.",
    formats: "Stories، Reel سريع، صور عفوية.",
    videoExample: "كواليس جلسة تصوير منتج في استوديو.",
    jlmUse: "تجهيز طلبيات للمحلات، زيارة فريق JLM لكراج، تصوير فيديو تعليمي من الكواليس.",
    hook: "«هيك بنجهّز طلبيات الكراجات كل صبح»",
    cta: "تابعنا لتشوف أكثر",
    purposeful: false,
    viral: false,
  },
  {
    key: "memes",
    nameEn: "Memes",
    nameAr: "ميمز",
    stage: "TOFU",
    definition: "قالب ميم معروف مُسقَط على موقف يعيشه الجمهور مع سيارته.",
    purpose: "مشاركة وانتشار عالي بتكلفة صفر؛ يجعل العلامة قريبة ومرحة.",
    formats: "صورة، Reel ميم، Story.",
    videoExample: "ميم Drake: يرفض «1 بـ 999» ويوافق «3 بـ 999» لإعلان تخفيضات ماكينة حلاقة.",
    jlmUse: "الميكانيكي اللي بسمع «صوت غريب» من الزبون، تأجيل تغيير الزيت، لمبة المحرك.",
    hook: "الميم نفسه هو الخطاف — نص قصير بلهجة فلسطينية.",
    cta: "منشن حدا بيعمل هيك 😅",
    purposeful: false,
    viral: true,
    guardrail: "قوالب ميم آمنة الحقوق؛ لا سخرية من منافس أو من الزبون.",
  },
  {
    key: "celebrity",
    nameEn: "Celebrity",
    nameAr: "مشاهير / مؤثرون",
    stage: "TOFU",
    definition: "شخصية معروفة تظهر مع المنتج أو تذكره.",
    purpose: "استعارة انتباه وثقة الجمهور المسبقة للشخصية؛ قفزة وعي سريعة.",
    formats: "إعلان مدفوع، Reel تعاون (Collab)، صورة.",
    videoExample: "إعلان آيس كريم بنجمة بوليوود.",
    jlmUse: "ميكانيكي أو صانع محتوى سيارات فلسطيني معروف، أو سائق رالي محلي.",
    hook: "«[اسم الشخصية] سألناه: شو أول إشي بتفحصه بسيارتك؟»",
    cta: "شوف التجربة كاملة",
    purposeful: false,
    viral: true,
    guardrail: "اتفاق مكتوب مع الشخصية؛ لا استخدام اسم أو صورة أي مشهور بدون إذن.",
  },
  {
    key: "billboard",
    nameEn: "Billboard",
    nameAr: "لوحة إعلانية (Billboard)",
    stage: "TOFU",
    definition: "رسالة قصيرة جدًا بخط كبير بأسلوب اللوحات الطرقية، حقيقية أو كموك-أب على صورة شارع.",
    purpose: "رسالة واحدة واضحة تُفهم في ثانية؛ يعطي إحساس علامة كبيرة.",
    formats: "صورة ثابتة، موك-أب لوحة في شارع محلي، Reel يقترب من اللوحة.",
    videoExample: "لوحة على جسر في شارع مزدحم: «Grocery runs don't need ten apps».",
    jlmUse: "موك-أب لوحة على دوار معروف بجملة واحدة عن مشكلة شائعة (استهلاك الوقود، صوت المحرك).",
    hook: "جملة اللوحة نفسها (6 كلمات كحد أقصى).",
    cta: "اسم العلامة + رابط/رقم فقط",
    purposeful: false,
    viral: false,
    guardrail: "إذا كانت موك-أب يجب ألا تُقدَّم كأنها لوحة حقيقية منشورة.",
  },
  {
    key: "event-announcement",
    nameEn: "Event announcement",
    nameAr: "إعلان فعالية",
    stage: "TOFU",
    definition: "إعلان عن حدث: ورشة، يوم فحص مجاني، معرض، إطلاق منتج، تواجد في محل.",
    purpose: "سبب للحديث والحضور؛ يربط العلامة بتجربة واقعية.",
    formats: "Reel إعلان، صورة بتاريخ ومكان، Stories عد تنازلي.",
    videoExample: "شخص يعلن فعالية وبيده تذاكر/بطاقات.",
    jlmUse: "يوم تدريب للميكانيكيين، تواجد JLM في محل قطع غيار بمدينة معينة.",
    hook: "«يوم [التاريخ] بنكون في [المكان] — تعال افحص سيارتك»",
    cta: "سجّل / احجز / تعال",
    purposeful: true,
    viral: false,
    guardrail: "لا تعلن فعالية غير مؤكدة التاريخ والمكان.",
  },
  {
    key: "founder-led",
    nameEn: "Founder led",
    nameAr: "محتوى يقوده المؤسس/المدير",
    stage: "TOFU",
    definition: "المؤسس أو مدير العلامة يتكلم مباشرة للكاميرا عن القصة، الرأي، أو سبب وجود المنتج.",
    purpose: "وجه بشري خلف العلامة؛ مصداقية وشخصية لا يقدر المنافس ينسخها.",
    formats: "Talking head Reel، فيديو طويل، بودكاست قصير.",
    videoExample: "صانعة محتوى/مؤسسة تتكلم للكاميرا وهي تحمل بطاقات.",
    jlmUse: "مدير JLM فلسطين يحكي ليش اختاروا هالمنتجات أو أكثر خطأ بشوفه عند السواقين.",
    hook: "«بعد [عدد] سنة بالسوق، هاد أكثر خطأ بشوفه…»",
    cta: "اسألني بالتعليقات",
    purposeful: true,
    viral: true,
    guardrail: "أي رقم سنوات أو خبرة يجب أن يكون موثقًا.",
  },
  {
    key: "phone-call-mockup",
    nameEn: "Phone call Mockup",
    nameAr: "موك-أب مكالمة هاتفية",
    stage: "TOFU",
    definition: "تصميم يشبه شاشة مكالمة واردة، اسم المتصل هو الفائدة أو المنتج.",
    purpose: "نمط مألوف يوقف التمرير؛ فضول «مين بيتصل؟».",
    formats: "صورة ثابتة، Story، Reel قصير مع صوت رنين.",
    videoExample: "AG1: «A life without bloating is calling…» مع زر Accept.",
    jlmUse: "«محرك أهدأ بيتصل فيك…» أو «فحص النجمة الناجح بيتصل» مع صورة المنتج الحقيقية.",
    hook: "اسم المتصل = النتيجة المرغوبة.",
    cta: "اسحب للرد / رد هلأ",
    purposeful: false,
    viral: true,
    guardrail: "النتيجة في اسم المتصل يجب أن تكون ادعاء مسموحًا وموثقًا.",
  },
  {
    key: "news-mockup",
    nameEn: "News mockup",
    nameAr: "موك-أب خبر عاجل",
    stage: "TOFU",
    definition: "تصميم بشكل خبر عاجل أو عنوان صحفي.",
    purpose: "إلحاح وفضول؛ يحوّل معلومة عادية إلى «خبر».",
    formats: "صورة، Reel بشريط أخبار.",
    videoExample: "شريط «Breaking News» على صورة بأسلوب صفحة إخبارية.",
    jlmUse: "«عاجل: ميكانيكي في نابلس بيكشف ليش سيارتك بتصرف بنزين أكثر» (عنوان تعليمي ساخر).",
    hook: "«عاجل:» + معلومة مفاجئة.",
    cta: "اقرأ التفاصيل بالكابشن",
    purposeful: false,
    viral: true,
    guardrail: "يجب أن يكون واضحًا أنه أسلوب إبداعي وليس خبرًا حقيقيًا؛ لا تقليد لعلامة وسيلة إعلام حقيقية.",
  },

  // ───────────── MOFU — الاعتبار والثقة ─────────────
  {
    key: "comment-response",
    nameEn: "Comment Response",
    nameAr: "الرد على تعليق",
    stage: "MOFU",
    definition: "فيديو أو تصميم يبدأ بلقطة تعليق/سؤال حقيقي من الجمهور ثم يرد عليه.",
    purpose: "يثبت أن العلامة تسمع؛ يجيب الاعتراض أمام الجميع؛ يشجع على تعليقات أكثر.",
    formats: "Reel يبدأ بـ «Reply to comment»، Story، صورة «Ask me anything».",
    videoExample: "AG1: صندوق «Ask me anything» — «كيف أظل صحي وأنا مشغول؟» والرد بالفوائد.",
    jlmUse: "الرد على «هل الإضافات بتخرب المحرك؟» أو «بنفع للديزل؟» بتعليق حقيقي.",
    hook: "لقطة التعليق نفسه: «[اسم] سأل: …»",
    cta: "اكتب سؤالك وبنرد عليه بفيديو",
    purposeful: true,
    viral: false,
    guardrail: "التعليق يجب أن يكون حقيقيًا (بإذن أو بإخفاء الاسم)، لا تعليقات مؤلفة.",
  },
  {
    key: "case-studies",
    nameEn: "Case Studies",
    nameAr: "دراسات حالة",
    stage: "MOFU",
    definition: "قصة عميل/كراج واحد: المشكلة، ما تم عمله، النتيجة المقاسة.",
    purpose: "دليل عملي قابل للتصديق؛ يجعل المهتم يرى نفسه في القصة.",
    formats: "مقابلة فيديو، كاروسيل قصة، مقال.",
    videoExample: "مقابلة مع شريك مؤسس لعلامة ملابس: «كيف تبني شركة مربحة…».",
    jlmUse: "كراج في الخليل استخدم منتج على سيارات أجرة: المشكلة ← الاستخدام ← النتيجة كما قاسها.",
    hook: "«سيارة تكسي، 400 ألف كم، وكانت [المشكلة]…»",
    cta: "بدك نفس الحل؟ راسلنا",
    purposeful: true,
    viral: false,
    guardrail: "حالات حقيقية فقط بموافقة صاحبها ونتائج كما قيست فعلًا — لا قصص نجاح وهمية.",
  },
  {
    key: "certification-badges",
    nameEn: "Certification Badges",
    nameAr: "شارات الاعتماد والشهادات",
    stage: "MOFU",
    definition: "إبراز شهادة أو اعتماد أو مواصفة رسمية مع المنتج.",
    purpose: "يختصر الثقة بإثبات طرف ثالث؛ يحل اعتراض «هل هو أصلي/مضمون؟».",
    formats: "صورة منتج مع الشارة، كاروسيل شرح الشهادة.",
    videoExample: "Thorne: «The label says plant. The stats say performance.» مع شارة NSF Certified for Sport.",
    jlmUse: "إبراز أي اعتماد أو مواصفة موثقة للمنتج في قاعدة المعرفة (مثل التصنيع في بلد المنشأ أو موافقات المصنع).",
    hook: "«الملصق بيقول [x]. الشهادة بتقول [y].»",
    cta: "اعرف أكثر عن المنتج",
    purposeful: true,
    viral: false,
    guardrail: "فقط الشهادات الموجودة فعليًا في قاعدة المعرفة؛ لا رسم شارات غير ممنوحة.",
  },
  {
    key: "educational",
    nameEn: "Educational",
    nameAr: "تعليمي",
    stage: "MOFU",
    definition: "شرح معلومة مفيدة تحل مشكلة أو تصحح فهمًا خاطئًا، والمنتج جزء من الحل.",
    purpose: "قيمة أولًا؛ يبني مرجعية ويستحق الحفظ والمشاركة.",
    formats: "كاروسيل، Reel شرح، إنفوغرافيك.",
    videoExample: "مكمل Resveratrol: «أقرب لأهداف لياقتك» مع قائمة فوائد بأيقونات.",
    jlmUse: "ليش لمبة المحرك بتضوي، الفرق بين أنواع الزيت، علامات انسداد البخاخات.",
    hook: "«3 علامات إنه بخاخات سيارتك بدها تنظيف»",
    cta: "احفظ المنشور لترجعله",
    purposeful: true,
    viral: true,
  },
  {
    key: "expert-explainer",
    nameEn: "Expert Explainer",
    nameAr: "شرح خبير",
    stage: "MOFU",
    definition: "ميكانيكي أو مهندس أو خبير يشرح موضوعًا تقنيًا بلغة بسيطة.",
    purpose: "سلطة ومصداقية؛ يحول المعلومة التقنية إلى ثقة.",
    formats: "Talking head Reel في الكراج، فيديو أطول، مقطع من بودكاست.",
    videoExample: "خبير يشرح ضمن إعلان «You asked. We answered.».",
    jlmUse: "ميكانيكي معتمد يشرح متى تحتاج منظف نظام الوقود ومتى لا.",
    hook: "«كميكانيكي، هاد السؤال بنسأله كل يوم…»",
    cta: "إلك سؤال للخبير؟ اكتبه",
    purposeful: true,
    viral: false,
    guardrail: "الخبير شخص حقيقي بصفته الحقيقية؛ كلامه ضمن ادعاءات المنتج الموثقة.",
  },
  {
    key: "faqs",
    nameEn: "FAQs",
    nameAr: "أسئلة شائعة",
    stage: "MOFU",
    definition: "تجميع الأسئلة المتكررة من الرسائل والتعليقات والإجابة عنها.",
    purpose: "يزيل الاعتراضات قبل الشراء؛ يخفف ضغط خدمة العملاء.",
    formats: "كاروسيل سؤال/جواب، Reel «سألتونا وجاوبنا»، Highlight ثابت.",
    videoExample: "«You asked. We answered.» مع فقاعات أسئلة عن منتج عناية.",
    jlmUse: "«كل قديش بستعمله؟ بنفع مع الغاز؟ بأثر على الضمان؟» من أسئلة الواتساب الفعلية.",
    hook: "«سألتونا… وهاي الإجابات»",
    cta: "في سؤال ما جاوبناه؟ راسلنا",
    purposeful: true,
    viral: false,
  },
  {
    key: "how-to",
    nameEn: "How to",
    nameAr: "طريقة الاستخدام (How to)",
    stage: "MOFU",
    definition: "خطوات عملية مرقمة لاستخدام المنتج أو حل مشكلة.",
    purpose: "يزيل خوف «ما بعرف أستعمله»؛ يستحق الحفظ.",
    formats: "Reel خطوات، كاروسيل مرقم، فيديو مقسم لقطات.",
    videoExample: "خطوات روتين عناية: فتح المنتج ← التطبيق ← النتيجة.",
    jlmUse: "كيف تضيف منظف الوقود بالخطوات الصحيحة (الكمية، التوقيت، قبل التفويل).",
    hook: "«3 خطوات وبتخلص بأقل من دقيقة»",
    cta: "احفظه لأول مرة بتستعمله",
    purposeful: true,
    viral: false,
    guardrail: "الخطوات والكميات من تعليمات المصنع في قاعدة المعرفة فقط.",
  },
  {
    key: "podcast",
    nameEn: "Podcast",
    nameAr: "بودكاست / مقطع حواري",
    stage: "MOFU",
    definition: "مقطع قصير من حوار أطول (بودكاست أو مقابلة) مع ترجمة على الشاشة.",
    purpose: "عمق وثقة؛ صيغة رائجة تشعر الجمهور أنه يسمع نقاشًا حقيقيًا لا إعلانًا.",
    formats: "Reel مقطع حواري مع Captions، حلقة طويلة على يوتيوب.",
    videoExample: "ضيف بودكاست: «Stop Overpaying For Blood Tests» مع ترجمة كلمة بكلمة.",
    jlmUse: "جلسة حوار بين مدير JLM وميكانيكي عن أخطاء الصيانة في فلسطين، تقطع لعدة Reels.",
    hook: "أقوى جملة في الحلقة كعنوان أعلى الفيديو.",
    cta: "الحلقة كاملة على [المنصة]",
    purposeful: true,
    viral: true,
  },
  {
    key: "social-proof-collage",
    nameEn: "Social proof Collage",
    nameAr: "مجمّع الدليل الاجتماعي",
    stage: "MOFU",
    definition: "المنتج في الوسط محاطًا بلقطات تقييمات أو رسائل عملاء حقيقية.",
    purpose: "كثرة الشهادات في كادر واحد = إحساس «الكل جربه».",
    formats: "صورة ثابتة، كاروسيل، Story.",
    videoExample: "Tula SPF «meet your SPF holy grail» محاط بمراجعات 5 نجوم.",
    jlmUse: "لقطات رسائل واتساب من كراجات ومحلات (بإذن وإخفاء الأرقام) حول عبوة المنتج.",
    hook: "«شو بيحكوا الكراجات عن [المنتج]؟»",
    cta: "جرّبه بنفسك",
    purposeful: false,
    viral: false,
    guardrail: "رسائل وتقييمات حقيقية فقط بإذن؛ لا تقييمات مؤلفة أو أعداد غير موثقة.",
  },
  {
    key: "text-heavy-statics",
    nameEn: "Text Heavy statics",
    nameAr: "تصاميم نصية ثابتة",
    stage: "MOFU",
    definition: "تصميم يعتمد على نص كبير ذكي (فكرة/ملاحظة/مقارنة لغوية) مع صورة منتج صغيرة.",
    purpose: "يُقرأ كفكرة لا كإعلان؛ يعمل جيدًا بدون فيديو وبتكلفة إنتاج منخفضة.",
    formats: "صورة ثابتة، إعلان Feed.",
    videoExample: "Yakult: «أن تقف في الطابور دون أن تنظر لعربة الشخص أمامك… مستحيل. مثل مشاركة ياكولت.»",
    jlmUse: "ملاحظة يومية يعرفها كل سائق («أن تسمع صوتًا جديدًا في السيارة وتتجاهله… مستحيل») مع صورة المنتج.",
    hook: "الجملة نفسها — ملاحظة دقيقة من الحياة اليومية.",
    cta: "قصير أو بدون CTA؛ اسم المنتج يكفي",
    purposeful: false,
    viral: true,
  },

  // ───────────── BOFU — القرار والشراء ─────────────
  {
    key: "checkout-mockup",
    nameEn: "Check out mockup",
    nameAr: "موك-أب صفحة الدفع/الطلب",
    stage: "BOFU",
    definition: "تصميم يحاكي واجهة شراء: سلة، زر «اطلب الآن»، بث مباشر مع زر شراء.",
    purpose: "يجعل خطوة الشراء ملموسة وسهلة؛ يقلل الاحتكاك الذهني.",
    formats: "صورة، Story مع ملصق رابط، إعلان تحويل.",
    videoExample: "eBay Live: «Find your next fit live» مع زر Bid now.",
    jlmUse: "موك-أب محادثة واتساب: «بدي [المنتج]» ← «تم، بوصلك بكرة» لإظهار سهولة الطلب.",
    hook: "«الطلب صار بكبسة»",
    cta: "اطلب عبر واتساب الآن",
    purposeful: false,
    viral: false,
    guardrail: "يجب أن يعكس طريقة الطلب الحقيقية المتاحة فعلًا ومدة التوصيل الحقيقية.",
  },
  {
    key: "countdown",
    nameEn: "Countdown",
    nameAr: "عد تنازلي",
    stage: "BOFU",
    definition: "عداد أيام/ساعات لنهاية عرض أو لإطلاق منتج.",
    purpose: "إلحاح زمني حقيقي يدفع المتردد لاتخاذ القرار.",
    formats: "Story بملصق العد التنازلي، صورة، Reel.",
    videoExample: "«COUNTDOWN — New Product Launch 02:08» أيام وساعات.",
    jlmUse: "آخر 48 ساعة لعرض موسمي (قبل الشتاء/فحص الترخيص).",
    hook: "«باقي يومين بس»",
    cta: "اطلب قبل ما يخلص العرض",
    purposeful: false,
    viral: false,
    guardrail: "موعد نهاية حقيقي يُحترم؛ لا عدادات وهمية تتجدد.",
  },
  {
    key: "offer-first-banners",
    nameEn: "Offer first banners",
    nameAr: "بانر العرض أولًا",
    stage: "BOFU",
    definition: "العرض نفسه هو العنوان الأكبر (خصم، اشترِ 1 واحصل…) والباقي ثانوي.",
    purpose: "للجمهور الدافئ الذي يعرف المنتج: يكفيه سبب إضافي ليشتري الآن.",
    formats: "صورة إعلانية، Story، بانر موقع.",
    videoExample: "Buzzie: «Buy 1 Get 1 40% Off» بشكل إشعار هاتف.",
    jlmUse: "«اشترِ 2 من [المنتج] والثالث بنص السعر» لمحلات القطع.",
    hook: "العرض بالأرقام الغربية وبخط كبير.",
    cta: "اطلب الآن / الكمية محدودة (إن كانت فعلًا محدودة)",
    purposeful: false,
    viral: false,
    guardrail: "عروض معتمدة من الإدارة فقط وبشروط مكتوبة.",
  },
  {
    key: "product-image",
    nameEn: "Product Image",
    nameAr: "صورة المنتج",
    stage: "BOFU",
    definition: "المنتج هو البطل: صورة نظيفة مع رسالة قصيرة وعرض أو سعر.",
    purpose: "تذكير بصري بالمنتج للجاهز للشراء؛ أساس إعلانات إعادة الاستهداف والكتالوج.",
    formats: "صورة، كاروسيل منتجات، إعلان كتالوج.",
    videoExample: "Crystal Clear: «How it should be done» مع كود خصم 20%.",
    jlmUse: "عبوة المنتج الأصلية على خلفية نظيفة + المشكلة التي يحلها + طريقة الطلب.",
    hook: "«الحل اللي كنت بتدور عليه لـ[المشكلة]»",
    cta: "اطلب الآن",
    purposeful: false,
    viral: false,
    guardrail: "صورة المنتج الحقيقية فقط؛ لا تعديل على العبوة أو الشعار ولا توليد للمنتج.",
  },
  {
    key: "studio-shoots",
    nameEn: "Studio Shoots",
    nameAr: "تصوير استوديو",
    stage: "BOFU",
    definition: "تصوير احترافي بإضاءة استوديو، غالبًا مع شخص يتفاعل مع المنتج.",
    purpose: "يرفع القيمة المدركة ويبرر السعر؛ مظهر علامة محترمة.",
    formats: "صورة إعلانية، Reel منتج سينمائي.",
    videoExample: "عارضة تعانق عبوة سيروم كبيرة.",
    jlmUse: "تصوير منتجات JLM مع ميكانيكي بزي العمل بإضاءة استوديو.",
    hook: "صورة قوية بدل الكلام + سطر واحد.",
    cta: "اطلب الآن",
    purposeful: false,
    viral: false,
  },
  {
    key: "ugc-testimonials",
    nameEn: "UGC testimonials",
    nameAr: "شهادات العملاء (UGC)",
    stage: "BOFU",
    definition: "فيديو بكاميرا الموبايل لعميل حقيقي يحكي تجربته بأسلوبه.",
    purpose: "أقوى دليل قبل الشراء لأنه لا يبدو إعلانًا.",
    formats: "Reel عمودي، Story، إعلان مدفوع.",
    videoExample: "فتاة تمسك منتج عناية بالشعر وتتكلم للكاميرا («UGC example video»).",
    jlmUse: "صاحب سيارة أو ميكانيكي يحكي تجربته بلهجته من داخل الكراج.",
    hook: "أول جملة من العميل: «صرلي شهر بستعمله وهاد اللي صار…»",
    cta: "جرّبه أنت كمان — اطلب عبر واتساب",
    purposeful: true,
    viral: true,
    guardrail: "عملاء حقيقيون بموافقة مكتوبة؛ لا ممثلين يُقدَّمون كعملاء؛ إفصاح عن أي مقابل.",
  },
  {
    key: "price-comparison",
    nameEn: "Price comparison",
    nameAr: "مقارنة السعر/القيمة",
    stage: "BOFU",
    definition: "وضع تكلفة المنتج مقابل تكلفة بديل أو تكلفة المشكلة نفسها.",
    purpose: "يعيد تأطير السعر كتوفير؛ يجيب اعتراض «غالي».",
    formats: "صورة جنبًا إلى جنب، كاروسيل، Reel حساب.",
    videoExample: "عطران: «Same smell. Different receipt.» — $300 مقابل $49.",
    jlmUse: "سعر عبوة المنتج مقابل تكلفة إصلاح المشكلة في الكراج (بأسعار موثقة ومؤرخة).",
    hook: "«نفس [الغاية]… فاتورة مختلفة»",
    cta: "وفّر واطلب الآن",
    purposeful: true,
    viral: true,
    guardrail: "لا مقارنة باسم منافس في محتوى منشور؛ قارن بتكلفة المشكلة أو الإصلاح بأرقام موثقة ومؤرخة.",
  },
  {
    key: "fomo-offers",
    nameEn: "FOMO offers",
    nameAr: "عروض الخوف من الفوات (FOMO)",
    stage: "BOFU",
    definition: "عرض محدود بوقت أو كمية مع إبراز «لفترة محدودة».",
    purpose: "يحول النية إلى فعل الآن بدل «بعدين».",
    formats: "صورة «Limited Offer»، Story، إعلان.",
    videoExample: "«LIMITED OFFER 15% OFF» لمنتجات عناية.",
    jlmUse: "عرض لأول 50 كراج يطلب هذا الأسبوع (إن كان العرض فعلًا محدودًا).",
    hook: "«لفترة محدودة: …»",
    cta: "احجز طلبك قبل ما يخلص",
    purposeful: false,
    viral: false,
    guardrail: "الحد الزمني أو الكمي يجب أن يكون حقيقيًا؛ لا ندرة مصطنعة.",
  },
  {
    key: "freebies",
    nameEn: "Freebies",
    nameAr: "هدايا ومجاني مع الطلب",
    stage: "BOFU",
    definition: "شيء مجاني مع الشراء: منتج إضافي، عينة، فحص، توصيل مجاني.",
    purpose: "«مجاني» أقوى محفز نفسي؛ يرفع قيمة السلة.",
    formats: "صورة، Story، إعلان.",
    videoExample: "Noon × Alejon: «Buy 2 Get 2 Free» مع عربة تسوق.",
    jlmUse: "عينة منتج مجانية مع كل طلب لمحل قطع، أو توصيل مجاني فوق حد معين.",
    hook: "«اشترِ 2 وخذ 2 ببلاش»",
    cta: "اطلب الآن",
    purposeful: false,
    viral: true,
    guardrail: "عرض معتمد من الإدارة بشروط واضحة ومخزون متوفر.",
  },
];

const ORDER: FunnelStage[] = ["TOFU", "MOFU", "BOFU"];

function formatType(t: ContentType): string {
  const tags = [t.purposeful ? "هادف" : null, t.viral ? "قابل للانتشار" : null].filter(Boolean).join("، ");
  return [
    `- **${t.nameEn}** (${t.nameAr})${tags ? ` [${tags}]` : ""}: ${t.definition}`,
    `  الغرض: ${t.purpose} | الصيغ: ${t.formats}`,
    `  لـ JLM: ${t.jlmUse} | Hook: ${t.hook} | CTA: ${t.cta}`,
    t.guardrail ? `  ⚠️ شرط: ${t.guardrail}` : null,
  ]
    .filter(Boolean)
    .join("\n");
}

export const CONTENT_TYPES_SYSTEM_PROMPT = `
# مكتبة أنواع المحتوى حسب مرحلة القمع (28 نوعًا)
كل فكرة أو منشور أو صف في خطة محتوى يجب أن يحدد: مرحلة القمع (TOFU/MOFU/BOFU) + نوع المحتوى من هذه المكتبة بالاسم الإنجليزي كما هو. لا تخترع نوعًا خارجها إلا إذا طلب المستخدم ذلك، ولا تستخدم نفس النوع أكثر من مرتين متتاليتين.

قواعد عامة:
- المرحلة تحدد النوع والـ CTA والـ KPI: TOFU = وعي وانتشار، MOFU = ثقة وإقناع، BOFU = طلب الآن.
- التوزيع الافتراضي في أي خطة (ما لم يحدد المستخدم هدفًا آخر): 40% TOFU، 35% MOFU، 25% BOFU. عند إطلاق منتج جديد أو حساب جديد ارفع TOFU؛ في موسم عروض ارفع BOFU. وهذا التوزيع يتكامل مع نسب المحتوى الافتراضية (تعليمي/ترفيهي/بيعي/نتائج/قصص) ولا يلغيها.
- الأنواع الموسومة [هادف] تصلح للمحتوى الهادف (قيمة أولًا). الأنواع الموسومة [قابل للانتشار] تصلح للمحتوى الـ Viral.
- أي نوع عليه ⚠️ شرط: لا تقترحه إذا لم يتوفر الدليل المطلوب في قاعدة المعرفة — اذكر المعلومة الناقصة بدلًا من ذلك.

${ORDER.map(
  (stage) =>
    `## ${stage} — ${FUNNEL_STAGES[stage].ar}\nالهدف: ${FUNNEL_STAGES[stage].goal}\nمؤشرات القياس: ${FUNNEL_STAGES[stage].kpi}\n\n` +
    CONTENT_TYPES.filter((t) => t.stage === stage)
      .map(formatType)
      .join("\n"),
).join("\n\n")}
`.trim();
