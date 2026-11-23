/**
 * Edit-style library: 17 video editing styles, and which content types
 * (see content-types.ts) each one strengthens.
 *
 * Source: a 33-second Reel by Ram Ramez supplied by the owner (analysed
 * 2026-11-23). The 17 style names and their order are verbatim from the
 * video's on-screen checklist (FACT); the "seen" descriptions are what the
 * frames show. How-to-build notes, purposes, content-type pairings and
 * guardrails are our analysis (INSIGHT / RECOMMENDATION). Full write-up:
 * docs/content-types/edit-styles.md
 *
 * Single source of truth: the prompt block below is generated from
 * EDIT_STYLES. Static on every request, so compose.ts sends it inside the
 * cached frameworks block.
 */
import { CONTENT_TYPES } from "./content-types";

export type EditStyle = {
  key: string;
  nameEn: string;
  nameAr: string;
  /** Where it appears in the source video (mm:ss). */
  at: string;
  /** What the frames show. */
  seen: string;
  /** How to build it (CapCut / Premiere / After Effects level). */
  build: string;
  /** What it does for the viewer. */
  purpose: string;
  /** Content-type keys (content-types.ts) it suits best. */
  bestFor: string[];
  effort: "سهل" | "متوسط" | "متقدم";
  guardrail?: string;
};

export const EDIT_STYLES: EditStyle[] = [
  {
    key: "orbit",
    nameEn: "Orbit",
    nameAr: "مدار حول الرأس",
    at: "00:01–00:03",
    seen: "بطاقات صغيرة (Cut، Grade، Captions، Effects) تدور حول رأس المتحدث في مسار ثلاثي الأبعاد، بعضها أمامه وبعضها خلفه.",
    build: "عزل المتحدث (Remove background / Rotoscope) ووضعه بطبقة فوق البطاقات الخلفية وتحت الأمامية؛ تحريك البطاقات بـ Keyframes على مسار بيضاوي.",
    purpose: "خطاف بصري في أول 3 ثوانٍ يعرض مكونات الفكرة كلها مرة واحدة.",
    bestFor: ["founder-led", "educational", "expert-explainer", "how-to", "event-announcement"],
    effort: "متقدم",
  },
  {
    key: "couch-wall",
    nameEn: "Couch wall",
    nameAr: "جدار المحتوى خلف المتحدث",
    at: "00:03–00:05",
    seen: "خلفية المتحدث تتحول إلى جدار من صور مصغّرة لمنشورات/ريلز سابقة بينما يبقى هو في المقدمة.",
    build: "عزل المتحدث + شبكة صور (Grid) خلفه مع حركة بطيئة أو ظهور متتابع للصور.",
    purpose: "إثبات حجم العمل أو الانتشار بلقطة واحدة؛ «انظر كم عملنا».",
    bestFor: ["social-proof-collage", "case-studies", "behind-the-scenes", "founder-led", "ugc-testimonials"],
    effort: "متوسط",
    guardrail: "الصور في الجدار حقيقية (منشورات أو شهادات فعلية) لا لقطات مؤلفة.",
  },
  {
    key: "ui-world",
    nameEn: "UI world",
    nameAr: "عالم الواجهة",
    at: "00:05–00:07",
    seen: "نافذة برنامج/Terminal تظهر خلف المتحدث وتكتب أوامر («edit my reel») ثم تعرض التقدم.",
    build: "تصميم واجهة (لقطة شاشة أو Mockup) خلف المتحدث المعزول مع كتابة نص متحركة (Typewriter).",
    purpose: "يشرح عملية أو أداة كأن المشاهد يراها من الداخل.",
    bestFor: ["how-to", "educational", "checkout-mockup", "behind-the-scenes"],
    effort: "متوسط",
  },
  {
    key: "frame-break",
    nameEn: "Frame break",
    nameAr: "كسر الإطار",
    at: "00:07–00:09",
    seen: "الفيديو يصغر داخل إطار بحواف دائرية على خلفية داكنة، والمتحدث يبرز خارج حدود الإطار.",
    build: "تصغير اللقطة داخل إطار + نسخة معزولة من المتحدث فوق الإطار بحيث يتجاوز رأسه/جسمه الحافة.",
    purpose: "عمق ثلاثي الأبعاد يلفت العين؛ يصلح لتمييز لحظة مهمة.",
    bestFor: ["before-after", "product-image", "studio-shoots", "founder-led", "celebrity"],
    effort: "متوسط",
  },
  {
    key: "digital-zoom",
    nameEn: "Digital zoom",
    nameAr: "زوم رقمي (Punch-in)",
    at: "00:09–00:10",
    seen: "قفزة تقريب مفاجئة على الوجه من نفس اللقطة.",
    build: "Scale من 100% إلى 130–150% على قطع (Cut) أو بانتقال سريع؛ التصوير بدقة 4K يحافظ على الجودة.",
    purpose: "أبسط طريقة لكسر الرتابة والتأكيد على جملة مهمة.",
    bestFor: ["educational", "expert-explainer", "faqs", "comment-response", "founder-led", "podcast", "memes"],
    effort: "سهل",
  },
  {
    key: "full-mockup",
    nameEn: "Full mockup",
    nameAr: "موك-أب هاتف كامل",
    at: "00:10–00:12",
    seen: "هاتف ينزلق من طرف الشاشة ويعرض ريل/تطبيقًا بجانب المتحدث.",
    build: "إطار هاتف PNG + تسجيل شاشة داخله، يدخل بحركة Slide مع Ease.",
    purpose: "يعرض منشورًا، رسالة، أو تجربة طلب داخل سياق الهاتف المألوف.",
    bestFor: ["checkout-mockup", "phone-call-mockup", "comment-response", "ugc-testimonials", "news-mockup", "social-proof-collage"],
    effort: "سهل",
    guardrail: "ما يظهر داخل الهاتف حقيقي (رسالة/تعليق/صفحة طلب فعلية) أو موضح أنه تمثيل.",
  },
  {
    key: "checklist",
    nameEn: "Checklist",
    nameAr: "قائمة تحقق",
    at: "00:12–00:14",
    seen: "بطاقة بمربعات تتعبأ بعلامة ✓ واحدًا تلو الآخر («Cut the pauses، Add captions، Add 17 edits»).",
    build: "عناصر نص + مربعات تظهر بالتتابع مع صوت «تك» عند كل علامة.",
    purpose: "يحول الخطوات أو الفوائد إلى تقدم مرئي مُرضٍ؛ سهل الحفظ.",
    bestFor: ["how-to", "faqs", "educational", "freebies", "offer-first-banners"],
    effort: "سهل",
  },
  {
    key: "headline-wall",
    nameEn: "Headline wall",
    nameAr: "جدار العناوين والأرقام",
    at: "00:14–00:16",
    seen: "أرقام وعبارات ضخمة تظهر متتابعة بجانب المتحدث: «17 edits / 0 editors / 1 prompt».",
    build: "Kinetic typography: أرقام كبيرة بلون العلامة تظهر بـ Pop أو Slide على إيقاع الكلام.",
    purpose: "يرسخ الرسالة في أرقام قليلة يتذكرها المشاهد.",
    bestFor: ["text-heavy-statics", "case-studies", "price-comparison", "certification-badges", "billboard", "news-mockup"],
    effort: "سهل",
    guardrail: "كل رقم يظهر يجب أن يكون موثقًا في قاعدة المعرفة.",
  },
  {
    key: "zoom-through-cut",
    nameEn: "Zoom through cut",
    nameAr: "قطع بالزوم العابر",
    at: "00:16–00:18",
    seen: "تقريب شديد جدًا حتى يملأ الوجه الشاشة ثم قطع إلى لقطة واسعة.",
    build: "Zoom in سريع مع Motion blur على آخر فريمات المقطع، ثم Cut للقطة التالية (أو Zoom out منها).",
    purpose: "انتقال بطاقة عالية يربط فكرتين ويمنع الملل.",
    bestFor: ["memes", "before-after", "founder-led", "countdown", "fomo-offers"],
    effort: "سهل",
  },
  {
    key: "chart-grow",
    nameEn: "Chart grow",
    nameAr: "رسم بياني ينمو",
    at: "00:18–00:20",
    seen: "خط رسم بياني برتقالي يصعد خلف المتحدث بعنوان «views» وينتهي بـ «+840%».",
    build: "خط بياني (Shape layer أو Trim path) يُرسم تدريجيًا مع عداد رقم يرتفع.",
    purpose: "يجعل النتيجة أو التحسن ملموسًا ومقنعًا.",
    bestFor: ["case-studies", "price-comparison", "educational", "before-after"],
    effort: "متوسط",
    guardrail: "البيانات حقيقية ومقاسة فقط؛ لا رسوم بيانية توضيحية تبدو كنتائج.",
  },
  {
    key: "pull-back-reveal",
    nameEn: "Pull back reveal",
    nameAr: "الكشف بالابتعاد",
    at: "00:20–00:22",
    seen: "الكاميرا «تبتعد» فيتضح أن الفيديو يُعرض داخل واجهة برنامج مونتاج مع شريط زمني وحالة «17/17 edits applied».",
    build: "Scale down للفيديو داخل تصميم واجهة/شاشة/هاتف أكبر، مع حركة سلسة.",
    purpose: "لحظة مفاجأة تكشف «الكواليس» أو السياق الحقيقي.",
    bestFor: ["behind-the-scenes", "checkout-mockup", "how-to", "case-studies"],
    effort: "متوسط",
  },
  {
    key: "green-screen",
    nameEn: "Green screen",
    nameAr: "استبدال الخلفية",
    at: "00:22–00:24",
    seen: "خلفية الشرفة تتحول إلى استوديو أبيض نظيف والمتحدث كما هو.",
    build: "Remove background (CapCut/Premiere) أو كروما حقيقية، ثم وضع خلفية جديدة مع ظل خفيف.",
    purpose: "ينقل المتحدث إلى أي مكان: كراج، محل قطع، صورة المنتج، أو خبر.",
    bestFor: ["comment-response", "news-mockup", "studio-shoots", "expert-explainer", "celebrity"],
    effort: "سهل",
    guardrail: "لا خلفيات توحي بمكان أو حدث لم يحصل (مثلًا معرض لم نشارك فيه).",
  },
  {
    key: "paper-cut",
    nameEn: "Paper cut",
    nameAr: "قص ورقي (كولاج)",
    at: "00:24–00:25",
    seen: "المتحدث بحدود بيضاء كالملصق فوق خلفية أشكال ورقية ملونة (برتقالي، كريمي، أزرق).",
    build: "عزل المتحدث + Stroke أبيض سميك + خلفية كولاج أشكال مسطحة.",
    purpose: "مظهر يدوي مرح يميز المحتوى عن الإعلانات التقليدية.",
    bestFor: ["memes", "educational", "faqs", "event-announcement", "freebies"],
    effort: "متوسط",
  },
  {
    key: "doodle-boil",
    nameEn: "Doodle boil",
    nameAr: "رسومات يدوية متحركة",
    at: "00:26–00:27",
    seen: "رسومات بيضاء مرسومة باليد (تاج، نجوم، خطوط متموجة) تهتز حول رأس المتحدث.",
    build: "رسومات بخط يدوي بـ 2–3 نسخ مختلفة قليلًا تتبدل كل 2–3 فريمات (Boil effect).",
    purpose: "يضيف شخصية وفكاهة ويوجه العين لنقطة معينة.",
    bestFor: ["memes", "founder-led", "comment-response", "before-after", "freebies"],
    effort: "متوسط",
  },
  {
    key: "vertigo",
    nameEn: "Vertigo",
    nameAr: "دولي زوم (Vertigo)",
    at: "00:27–00:29",
    seen: "المتحدث ثابت الحجم بينما الخلفية تتمدد وتبتعد، إحساس دوار سينمائي.",
    build: "أثناء التصوير: تحريك الكاميرا للخلف مع تقريب العدسة. في المونتاج: عزل المتحدث وتكبير الخلفية بعكس اتجاهه.",
    purpose: "لحظة درامية لكشف مفاجأة أو مشكلة.",
    bestFor: ["news-mockup", "before-after", "countdown", "fomo-offers", "founder-led"],
    effort: "متقدم",
  },
  {
    key: "cover-story",
    nameEn: "Cover story",
    nameAr: "غلاف مجلة",
    at: "00:29–00:31",
    seen: "تصميم غلاف مجلة: اسم ضخم خلف الرأس، سطر «The edits issue · Nov 2026» وعبارة «No editor needed.».",
    build: "عزل المتحدث + Masthead بخط Serif كبير خلفه + عناوين صغيرة كغلاف مجلة.",
    purpose: "يعطي قيمة ومكانة؛ ممتاز لإعلان أو قصة شخصية.",
    bestFor: ["founder-led", "celebrity", "event-announcement", "case-studies", "studio-shoots"],
    effort: "متوسط",
    guardrail: "لا تقليد لاسم أو شعار مجلة حقيقية.",
  },
  {
    key: "glass-type",
    nameEn: "Glass type",
    nameAr: "نص زجاجي",
    at: "00:31–00:33",
    seen: "كلمة ضخمة «EDITS» بتأثير زجاج شفاف ضبابي خلف المتحدث.",
    build: "نص كبير مع Blur للخلفية خلفه + حدود فاتحة (Glassmorphism)، والمتحدث المعزول أمامه.",
    purpose: "ختام أنيق يثبت الكلمة المفتاحية أو اسم المنتج.",
    bestFor: ["product-image", "studio-shoots", "billboard", "text-heavy-statics", "offer-first-banners"],
    effort: "متوسط",
  },
];

/** Edit styles that suit a given content type, derived from bestFor. */
export function editStylesFor(contentTypeKey: string): EditStyle[] {
  return EDIT_STYLES.filter((s) => s.bestFor.includes(contentTypeKey));
}

const typeName = (key: string) => CONTENT_TYPES.find((t) => t.key === key)?.nameEn ?? key;

export const EDIT_STYLES_SYSTEM_PROMPT = `
# مكتبة ستايلات المونتاج (17 ستايلًا)
عند كتابة أي فيديو (Reel/TikTok/Story/إعلان فيديو) أو صف فيديو في خطة محتوى: اقترح 2–4 ستايلات مونتاج من هذه المكتبة بالاسم الإنجليزي، وحدد أين يدخل كل ستايل في الفيديو (الثانية أو المشهد) ولماذا. قواعد:
- أول 3 ثوانٍ: ستايل خطاف قوي (مثل Orbit، Zoom through cut، Vertigo، Frame break، Doodle boil).
- الوسط: ستايل يشرح أو يثبت (مثل Checklist، Headline wall، Chart grow، Full mockup، UI world).
- الختام: ستايل يثبت الرسالة أو المنتج (مثل Glass type، Cover story، Pull back reveal).
- لا تكدس أكثر من ستايل متقدم واحد في فيديو قصير؛ Digital zoom كل 3–5 ثوانٍ يكفي لكسر الرتابة.
- حافظ على هوية JLM: ألوان العلامة في النصوص والبطاقات، خط واحد ثابت، وصورة المنتج الحقيقية دون تعديل على العبوة أو الشعار.
- أي ستايل يعرض أرقامًا أو نتائج أو رسائل عملاء (⚠️) يحتاج بيانات حقيقية من قاعدة المعرفة.

${EDIT_STYLES.map((s) =>
  [
    `- **${s.nameEn}** (${s.nameAr}، ${s.effort}): ${s.seen}`,
    `  التنفيذ: ${s.build} | الفائدة: ${s.purpose}`,
    `  الأنسب لـ: ${s.bestFor.map(typeName).join("، ")}`,
    s.guardrail ? `  ⚠️ شرط: ${s.guardrail}` : null,
  ]
    .filter(Boolean)
    .join("\n"),
).join("\n")}
`.trim();
