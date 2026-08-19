import { PrismaClient, type Prisma } from "../src/generated/prisma/client";
import { PrismaLibSql } from "@prisma/adapter-libsql";
import bcrypt from "bcryptjs";

const adapter = new PrismaLibSql({ url: process.env.DATABASE_URL ?? "file:./dev.db" });
const prisma = new PrismaClient({ adapter });

type SwotJson = { s: string; w: string; o: string; t: string };
type TowsJson = { so: string; wo: string; st: string; wt: string };

type CompetitorSeed = {
  name: string;
  country: string | null;
  foundedYear: number | null;
  localDistributor: string | null;
  tier: number;
  pricingTier: string;
  threatRating: number;
  productCategories: string[];
  strengths: string[];
  weaknesses: string[];
  swot: SwotJson;
  tows: TowsJson;
  opportunitiesForJlm: string[];
  marketingMessage: string;
};

// Sourced verbatim (translated field-by-field, not paraphrased) from
// "COMPETITOR ANALYSIS (JLM).docx" — all 17 competitors it profiles.
const COMPETITORS: CompetitorSeed[] = [
  {
    name: "Liqui Moly",
    country: "ألمانيا",
    foundedYear: 1957,
    localDistributor: "شركة واصف الحاج أحمد عامر (نابلس)",
    tier: 1,
    pricingTier: "premium",
    threatRating: 5,
    productCategories: [
      "Petrol Injector Cleaner", "Diesel Injector Cleaner", "Fuel System Cleaner",
      "Engine Flush", "Oil Additives", "Ceratec", "MOS2", "DPF Protector",
      "Catalytic System Cleaner", "Valve Protection", "Hydraulic Lifter Additive",
      "Motor Oil Saver", "Gear Oil Stop Leak",
    ],
    strengths: [
      "علامة تجارية عالمية ذات سمعة قوية",
      "تصنيع ألماني بالكامل",
      "تشكيلة كبيرة جدًا من المنتجات (أكثر من 4000 منتج عالميًا)",
      "وكيل قوي وراسخ في الضفة الغربية بشبكة توزيع واسعة",
      "تغطية لجميع فئات إضافات المحركات تقريبًا",
      "ثقة مرتفعة لدى الكراجات ومحلات قطع الغيار",
    ],
    weaknesses: [
      "أسعار أعلى من كثير من المنافسين",
      "كثرة المنتجات قد تربك العميل العادي في اختيار المنتج المناسب",
      "التركيز التسويقي الأكبر على الزيوت قد يجعل بعض الإضافات أقل بروزًا من العلامات المتخصصة",
    ],
    swot: {
      s: "علامة قوية، جودة ألمانية، تنوع كبير، وكيل قوي، انتشار واسع.",
      w: "أسعار مرتفعة، تعقيد في اختيار المنتج بسبب كثرة الخيارات.",
      o: "نمو الطلب على الإضافات الاحترافية مع زيادة أعمار المركبات واعتماد الصيانة الوقائية.",
      t: "دخول علامات أقل سعرًا، المنافسة من علامات متخصصة مثل JLM وWynn's، وتقلبات القدرة الشرائية.",
    },
    tows: {
      so: "استغلال قوة العلامة التجارية وشبكة الوكيل لتوسيع مبيعات الإضافات الاحترافية.",
      wo: "تبسيط رسائل التسويق وتوضيح استخدام كل منتج لتقليل حيرة العملاء.",
      st: "الاعتماد على السمعة الألمانية والجودة لمواجهة المنافسين الأقل سعرًا.",
      wt: "تقديم عروض أو حزم تجمع الزيوت مع الإضافات لتقليل أثر المنافسة السعرية.",
    },
    opportunitiesForJlm: [
      "التركيز على التخصص: إبراز أن JLM علامة متخصصة في الإضافات",
      "تبسيط اختيار المنتج عبر دليل أو تطبيق",
      "التدريب الفني للكراجات وشهادات اعتماد",
      "إبراز نتائج الاختبارات والمقارنات على منتجات مثل DPF وInjector Cleaner",
    ],
    marketingMessage:
      "Made in Germany — الجودة الألمانية، حماية المحرك، زيادة عمر المحرك، الأداء العالي، منتجات احترافية للكراجات",
  },
  {
    name: "Wynn's",
    country: "بلجيكا",
    foundedYear: 1939,
    localDistributor: "مجموعة استرادا (Strada Group) — بيت جالا، بيت لحم",
    tier: 1,
    pricingTier: "mid",
    threatRating: 5,
    productCategories: [
      "Petrol Injector Cleaner", "Diesel Injector Cleaner", "Fuel System Cleaner",
      "Engine Treatment", "Engine Flush", "Oil Additives", "DPF / Petrol System Treatments",
      "EGR & Intake Treatments", "Cooling System Flush", "Automatic Transmission Additives",
      "Stop Leak Products", "Turbo / Friction Protection",
    ],
    strengths: [
      "علامة متخصصة في إضافات المحركات وليست مجرد شركة زيوت",
      "خبرة عالمية طويلة في المعالجات الكيميائية",
      "تشكيلة واسعة جدًا من منتجات الإضافات",
      "وكيل نشط في التسويق الرقمي وعرض المنتجات باستمرار",
      "شبكة توزيع جيدة في الضفة الغربية",
    ],
    weaknesses: [
      "الوعي بالعلامة التجارية لدى المستهلك النهائي أقل من Liqui Moly",
      "الاعتماد التسويقي الأكبر على الوكيل المحلي",
      "بعض المنتجات متخصصة وتتطلب معرفة فنية من البائع لشرح استخدامها",
    ],
    swot: {
      s: "علامة متخصصة، خبرة طويلة، مجموعة كبيرة من المعالجات، وكيل نشط وشبكة توزيع قوية.",
      w: "انتشار العلامة لدى المستهلك النهائي أقل من بعض المنافسين الألمان، وعدم توفر أسعار منشورة يزيد صعوبة المقارنة.",
      o: "ازدياد الطلب على الصيانة الوقائية، وتوسع الكراجات في استخدام المعالجات الكيميائية بدلاً من الإصلاحات المكلفة.",
      t: "المنافسة من علامات متخصصة مثل JLM، ومن علامات قوية مثل Liqui Moly، بالإضافة إلى المنتجات منخفضة السعر.",
    },
    tows: {
      so: "استغلال التخصص والخبرة الطويلة مع شبكة استرادا لتوسيع استخدام المنتجات داخل الكراجات ومراكز الخدمة.",
      wo: "زيادة التوعية المباشرة للمستهلك النهائي وتبسيط شرح استخدام المنتجات.",
      st: "التركيز على كون Wynn's متخصصة في المعالجات الكيميائية لمواجهة العلامات التي تعتمد على قوة اسمها العام.",
      wt: "تعزيز برامج تدريب البائعين والكراجات لتقليل أثر المنافسة السعرية والمنتجات الأرخص.",
    },
    opportunitiesForJlm: [
      "إبراز الاعتمادات الفنية إن وجدت لمنتجات JLM أمام الكراجات",
      "التركيز على النتائج العملية عبر عروض وتجارب ميدانية",
      "برامج ولاء للكراجات عبر التدريب والدعم الفني والحوافز",
      "تبسيط الاختيار عبر دليل أو تطبيق يساعد الفنيين",
    ],
    marketingMessage:
      "بديل اقتصادي للإصلاحات الميكانيكية، استعادة أداء المحرك، تقليل استهلاك الوقود، حلول كيميائية احترافية سهلة الاستخدام",
  },
  {
    name: "Profi-Car",
    country: "ألمانيا",
    foundedYear: null,
    localDistributor: "Q.S. Company of Importing — القدس",
    tier: 2,
    pricingTier: "mid",
    threatRating: 4,
    productCategories: [
      "Petrol Injector Cleaner", "Diesel Injector Cleaner", "Fuel System Cleaner",
      "Engine Flush", "Oil Additives", "Radiator Additives", "Fuel Treatments",
      "Stop Leak", "Engine Protection Additives", "Car Care Chemicals",
    ],
    strengths: [
      "علامة ألمانية",
      "أسعار منافسة مقارنة بـ Liqui Moly",
      "محفظة متكاملة (زيوت + إضافات + منتجات عناية)",
      "وكيل رسمي معتمد في فلسطين",
      "انتشار جيد عبر شبكة موزعين محليين",
    ],
    weaknesses: [
      "الوعي بالعلامة التجارية أقل من Liqui Moly وWynn's",
      "الاعتماد الكبير على قوة الموزعين المحليين أكثر من التسويق المباشر",
      "محدودية المحتوى الفني والتسويقي الموجه للمستهلك مقارنة بالمنافسين العالميين",
    ],
    swot: {
      s: "جودة ألمانية، أسعار مناسبة، شبكة توزيع جيدة، تنوع في المنتجات.",
      w: "شهرة أقل، تسويق أقل، اعتماد كبير على الموزعين.",
      o: "استقطاب الكراجات التي تبحث عن بديل ألماني أقل تكلفة، والتوسع في المدن التي لا تغطيها العلامات الأكبر بقوة.",
      t: "المنافسة من Liqui Moly وWynn's وJLM، إضافة إلى العلامات الاقتصادية منخفضة السعر.",
    },
    tows: {
      so: "توسيع شبكة الموزعين والاستفادة من السعر التنافسي لزيادة الحصة السوقية.",
      wo: "الاستثمار في التسويق الرقمي والتدريب الفني لرفع الوعي بالعلامة.",
      st: "استخدام ميزة الجودة الألمانية مقابل سعر مناسب لمواجهة العلامات الأعلى سعرًا.",
      wt: "تقوية العلاقة مع الموزعين والكراجات للحفاظ على الولاء وتقليل أثر المنافسة.",
    },
    opportunitiesForJlm: [
      "إبراز التخصص في إضافات المحركات مقابل محفظة Profi-Car الأوسع",
      "التفوق الفني عبر نتائج اختبارات وشهادات أداء",
      "بناء برامج تدريب ودعم للكراجات",
      "زيادة التسويق المباشر للمستهلك النهائي",
    ],
    marketingMessage:
      "Made in Germany، الجودة الألمانية، حماية المحرك، قيمة عالية مقابل السعر، تشكيلة متكاملة من الزيوت والإضافات ومنتجات العناية",
  },
  {
    name: "Würth",
    country: "ألمانيا",
    foundedYear: 1945,
    localDistributor: "الفلسطينية للمحركات (PMC) — رام الله",
    tier: 2,
    pricingTier: "premium",
    threatRating: 4,
    productCategories: [
      "Petrol Injector Cleaner", "Diesel Injector Cleaner", "Fuel System Cleaner",
      "Engine Flush", "Oil Additives", "DPF Cleaner", "EGR / Intake Cleaner",
      "Radiator Products", "Transmission Additives", "Engine Treatments",
    ],
    strengths: [
      "علامة ألمانية ذات سمعة عالمية",
      "جودة عالية وثقة كبيرة لدى الفنيين",
      "محفظة واسعة من المواد الكيميائية الاحترافية",
      "دعم من وكيل قوي في قطاع السيارات",
      "حضور قوي داخل الورش والكراجات",
    ],
    weaknesses: [
      "تركيز أقل على التسويق للمستهلك النهائي",
      "أسعار مرتفعة مقارنة ببعض المنافسين",
      "انتشار محدود نسبيًا في محلات قطع الغيار مقارنة بـ Liqui Moly",
      "الاعتماد على شبكة الورش المهنية أكثر من البيع المفتوح",
    ],
    swot: {
      s: "علامة عالمية، جودة عالية، ثقة الفنيين، تركيز على القطاع الاحترافي، دعم من وكيل قوي.",
      w: "أسعار مرتفعة، حضور أقل لدى المستهلك النهائي، انتشار محدود في البيع بالتجزئة.",
      o: "زيادة عدد الورش المتخصصة، والطلب على المنتجات الاحترافية مع تعقيد أنظمة السيارات الحديثة.",
      t: "المنافسة من JLM وLiqui Moly وWynn's، إضافة إلى البدائل الأقل سعرًا.",
    },
    tows: {
      so: "توسيع التعاون مع الورش المعتمدة واستغلال السمعة المهنية للعلامة.",
      wo: "زيادة الوعي لدى أصحاب السيارات وتوسيع التواجد في محلات قطع الغيار.",
      st: "التركيز على الجودة والاعتمادية لمواجهة المنافسة السعرية.",
      wt: "تعزيز برامج التدريب والدعم الفني للحفاظ على ولاء الورش وتقليل انتقالها إلى علامات منافسة.",
    },
    opportunitiesForJlm: [
      "التوسع خارج الورش نحو محلات قطع الغيار والمستهلك النهائي",
      "إبراز التخصص في إضافات المحركات مقابل محفظة Würth الصناعية الأوسع",
      "إنتاج محتوى فني وتجارب ميدانية خاصة بأنظمة الوقود وDPF",
      "الشراكة مع الكراجات المستقلة غير المرتبطة بعلامات أخرى",
    ],
    marketingMessage:
      "الجودة الألمانية، حلول احترافية للورش، الاعتمادية، رفع كفاءة أعمال الصيانة، منتجات مخصصة للمهنيين",
  },
  {
    name: "Motul",
    country: "فرنسا",
    foundedYear: 1853,
    localDistributor: null,
    tier: 2,
    pricingTier: "premium",
    threatRating: 4,
    productCategories: [
      "Petrol Injector Cleaner", "Diesel System Cleaner", "Engine Flush",
      "Fuel System Cleaner", "DPF Cleaner", "Catalytic Converter Cleaner",
      "Oil Additives (محدود)", "Radiator Products",
    ],
    strengths: [
      "علامة عالمية معروفة",
      "سمعة قوية في الزيوت والأداء الرياضي",
      "جودة عالية",
      "توفر بعض منتجات الإضافات المطلوبة في السوق",
      "ثقة جيدة لدى شريحة من الفنيين",
    ],
    weaknesses: [
      "لا يوجد وكيل رسمي في الضفة",
      "توفر غير ثابت للمنتجات",
      "غياب الدعم الفني المحلي",
      "ضعف الأنشطة التسويقية المحلية",
    ],
    swot: {
      s: "علامة عالمية، جودة عالية، ثقة فنية.",
      w: "غياب وكيل رسمي، توفر غير مستقر، دعم محلي محدود.",
      o: "إمكانية زيادة الطلب عبر الاستيراد الموازي والسمعة العالمية.",
      t: "منافسة قوية من الوكلاء الرسميين مثل Liqui Moly وWynn's وJLM.",
    },
    tows: {
      so: "استغلال السمعة العالمية لزيادة المبيعات عبر التجار.",
      wo: "إنشاء شبكة توزيع رسمية مستقبلًا أو تعزيز دعم التجار.",
      st: "التركيز على الأداء والجودة لمواجهة المنافسين الرسميين.",
      wt: "تحسين استقرار التوريد لتقليل فقدان العملاء بسبب نقص المنتجات.",
    },
    opportunitiesForJlm: [
      "إبراز وجود وكيل رسمي ودعم فني محلي لدى JLM",
      "ضمان توفر المنتجات باستمرار",
      "تدريب الكراجات على منتجات JLM",
      "بناء ولاء الكراجات من خلال برامج دعم وتسويق",
    ],
    marketingMessage:
      "الأداء العالي، رياضة السيارات، الجودة الفرنسية، الاعتمادات الفنية من شركات السيارات، حماية المحرك",
  },
  {
    name: "MANNOL",
    country: "ألمانيا (SCT Germany)",
    foundedYear: 1993,
    localDistributor: null,
    tier: 3,
    pricingTier: "value",
    threatRating: 3,
    productCategories: [
      "Injector Cleaner", "Fuel System Cleaner", "Engine Flush", "Oil Additives",
      "Motor Doctor", "DPF Cleaner", "Catalytic Cleaner", "Radiator Additives",
    ],
    strengths: [
      "أسعار منخفضة",
      "تشكيلة واسعة",
      "انتشار جيد بين التجار",
      "توفر منتجات لمعظم فئات الإضافات",
    ],
    weaknesses: [
      "غياب وكيل رسمي",
      "تفاوت توفر المنتجات",
      "شهرة أقل في قطاع الإضافات الاحترافية مقارنة بـ JLM أو Wynn's",
      "محدودية الدعم الفني والتسويق المحلي",
    ],
    swot: {
      s: "سعر منخفض، تشكيلة جيدة، انتشار عبر التجار.",
      w: "لا يوجد وكيل رسمي، دعم فني وتسويق محدودان.",
      o: "استقطاب الشريحة الحساسة للسعر.",
      t: "منافسة العلامات Premium والوكلاء الرسميين، إضافة إلى تقلبات الاستيراد الموازي.",
    },
    tows: {
      so: "استغلال السعر المنخفض للتوسع لدى التجار والكراجات.",
      wo: "تحسين التواجد الرسمي وبناء شبكة توزيع مستقرة إذا دخلت الشركة رسميًا.",
      st: "الحفاظ على ميزة السعر مع تحسين جودة الرسائل التسويقية.",
      wt: "تقليل الاعتماد على الاستيراد الموازي لتثبيت توفر المنتجات.",
    },
    opportunitiesForJlm: [
      "التركيز على الجودة والاعتمادات الفنية بدلًا من منافسة السعر",
      "إبراز الدعم الفني المحلي والوكيل الرسمي",
      "استهداف الكراجات التي تبحث عن حلول طويلة الأمد",
      "توضيح الفارق في الأداء عبر تجارب ميدانية وشهادات استخدام",
    ],
    marketingMessage: "السعر المناسب، الجودة المقبولة، القيمة مقابل السعر، حلول اقتصادية للصيانة",
  },
  {
    name: "ABRO",
    country: "الولايات المتحدة الأمريكية",
    foundedYear: 1939,
    localDistributor: null,
    tier: 4,
    pricingTier: "value",
    threatRating: 3,
    productCategories: [
      "Fuel Injector Cleaner", "Fuel System Cleaner", "Diesel Injector Cleaner",
      "Diesel System Cleaner", "Engine Flush (Motor Flush)", "Oil Treatment",
      "Oil Stop Leak", "Smoke Stop", "Octane Booster", "Automatic Transmission Conditioner",
    ],
    strengths: [
      "علامة أمريكية معروفة عالميًا",
      "أسعار تنافسية",
      "منتجات سهلة الاستخدام ومتوفرة في عدة فئات",
      "قبول جيد لدى عدد من الكراجات",
      "توفر جيد عبر التجار والاستيراد الموازي",
    ],
    weaknesses: [
      "لا يوجد وكيل رسمي أو دعم فني محلي",
      "انتشار محدود في المنتجات المتخصصة مقارنة بـ JLM وWynn's",
      "الاعتماد على التجار يجعل التوفر غير ثابت",
      "الحضور التسويقي في الضفة الغربية ضعيف",
    ],
    swot: {
      s: "علامة أمريكية، أسعار مناسبة، تشكيلة جيدة من الإضافات الأساسية، قبول جيد لدى بعض الكراجات.",
      w: "غياب وكيل رسمي، دعم فني وتسويقي محدود، نقص في المنتجات المتخصصة مقارنة بالمنافسين الرئيسيين.",
      o: "إمكانية زيادة الانتشار عبر التجار والكراجات الباحثة عن بدائل اقتصادية.",
      t: "المنافسة من JLM وLiqui Moly وWynn's، إضافة إلى العلامات الاقتصادية الأخرى.",
    },
    tows: {
      so: "استغلال السعر المناسب وسمعة المنتج الأمريكي لزيادة الانتشار بين الكراجات.",
      wo: "تحسين التوزيع والدعم الفني إذا تم تعيين وكيل رسمي مستقبلًا.",
      st: "المحافظة على ميزة السعر مع التركيز على موثوقية الأداء.",
      wt: "تقليل أثر غياب الوكيل الرسمي عبر بناء شبكة موزعين أكثر استقرارًا.",
    },
    opportunitiesForJlm: [
      "إبراز التخصص في حلول DPF وEGR وTurbo مقابل الإضافات العامة لدى ABRO",
      "توفير تدريب ودعم فني وضمان استمرارية توفر المنتجات",
      "تقديم قيمة مضافة عبر إثبات الأداء بدل المنافسة السعرية المباشرة",
      "استخدام نتائج الاختبارات والشهادات الفنية لإقناع الورش",
    ],
    marketingMessage: "جودة أمريكية، سهولة الاستخدام، تحسين أداء المحرك، حلول صيانة اقتصادية",
  },
  {
    name: "BG Products",
    country: "الولايات المتحدة الأمريكية",
    foundedYear: 1971,
    localDistributor: null,
    tier: 1,
    pricingTier: "premium",
    threatRating: 5,
    productCategories: [
      "BG 44K Fuel System Cleaner (بنزين)", "BG Diesel Fuel Conditioner / BG245 (ديزل)",
      "Fuel System Cleaner", "Engine Flush", "Oil Additives", "Engine Performance Restoration",
      "EGR System Cleaner", "Intake System Cleaner", "Air Intake Cleaner",
      "Transmission Service Chemicals", "Cooling System Service", "MOA Oil Supplement",
    ],
    strengths: [
      "من أقوى العلامات المتخصصة عالميًا في إضافات المحركات",
      "سمعة ممتازة بين الميكانيكيين",
      "فعالية عالية في تنظيف أنظمة الوقود",
      "منتجات احترافية موجهة للورش",
      "ثقة كبيرة لدى عدد من الكراجات في السوق المحلي",
    ],
    weaknesses: [
      "لا يوجد وكيل رسمي في الضفة",
      "توفر المنتجات غير ثابت",
      "محدودية التسويق للمستهلك النهائي",
      "الاعتماد على قنوات غير رسمية للتوزيع",
    ],
    swot: {
      s: "علامة متخصصة، جودة عالية، ثقة قوية لدى الكراجات، نتائج مثبتة في خدمات تنظيف الوقود.",
      w: "غياب وكيل رسمي، توفر محدود، ضعف التسويق للمستهلك النهائي.",
      o: "نمو الطلب على خدمات تنظيف أنظمة الوقود والحقن في السيارات الحديثة.",
      t: "المنافسة من JLM وWynn's وLiqui Moly، وصعوبة الحفاظ على التوفر عبر الاستيراد الموازي.",
    },
    tows: {
      so: "استثمار السمعة الفنية القوية لتعزيز الانتشار بين الكراجات المتخصصة.",
      wo: "تحسين استقرار التوريد وتوسيع قنوات البيع إذا تم تعيين موزع رسمي مستقبلًا.",
      st: "الاعتماد على الأداء والنتائج العملية لمواجهة المنافسين ذوي الحملات التسويقية الأكبر.",
      wt: "تقليل أثر غياب الوكيل عبر دعم الكراجات بالمعلومات الفنية والمواد التدريبية.",
    },
    opportunitiesForJlm: [
      "إبراز الوكيل الرسمي لـ JLM وضمان التوفر والدعم الفني المستمر",
      "التوسع في تدريب الكراجات وبرامج شهادات الاعتماد",
      "التسويق المباشر للمستهلك النهائي",
      "نشر نتائج اختبارات ومقارنات على منتجات تنظيف البخاخات والديزل",
    ],
    marketingMessage: "حلول احترافية للكراجات، استعادة أداء المحرك، تقليل الانبعاثات، تنظيف كامل لأنظمة الوقود",
  },
  {
    name: "AUTOPROFI",
    country: "ألمانيا (bluechemGROUP)",
    foundedYear: null,
    localDistributor: "شركة الحواري التجارية — نابلس",
    tier: 2,
    pricingTier: "mid",
    threatRating: 4,
    productCategories: [
      "Petrol Injector Cleaner", "Diesel Injector Cleaner", "Fuel System Cleaner",
      "Engine Flush", "Oil Additives", "DPF Cleaner", "EGR / Intake Cleaner",
      "Radiator Products", "Automatic Transmission Products", "Power Steering Additives",
    ],
    strengths: [
      "علامة ألمانية تابعة لمجموعة متخصصة في كيميائيات السيارات",
      "تشكيلة واسعة من إضافات الوقود والزيت ومنتجات الصيانة",
      "وكيل معروف في قطاع قطع الغيار والزيوت",
      "تغطية جيدة لمعظم احتياجات الكراجات",
    ],
    weaknesses: [
      "شهرة العلامة لدى المستهلك النهائي أقل من Liqui Moly وWynn's",
      "الاعتماد بشكل كبير على قوة الوكيل المحلي",
      "حضور رقمي وتسويقي أقل من بعض المنافسين العالميين",
    ],
    swot: {
      s: "جودة ألمانية، محفظة منتجات متكاملة، وكيل قوي، سعر منافس.",
      w: "شهرة أقل من العلامات الكبرى، اعتماد على الوكيل في بناء العلامة محليًا.",
      o: "التوسع لدى الكراجات المستقلة وزيادة الطلب على الصيانة الوقائية.",
      t: "المنافسة من JLM وLiqui Moly وWynn's وBG، إضافة إلى العلامات الاقتصادية.",
    },
    tows: {
      so: "استغلال قوة الوكيل وتنوع المنتجات للتوسع في شبكة الكراجات.",
      wo: "زيادة الاستثمار في التسويق الفني والتوعية بالعلامة.",
      st: "إبراز الجودة الألمانية والسعر المنافس لمواجهة العلامات الأعلى سعرًا.",
      wt: "تعزيز ولاء الكراجات عبر التدريب والدعم الفني لتقليل تأثير المنافسين.",
    },
    opportunitiesForJlm: [
      "إبراز تخصص JLM الكامل في إضافات المحركات مقابل محفظة AUTOPROFI الأوسع",
      "التركيز على الاعتمادات ونتائج الاختبارات الفنية",
      "برامج ولاء للكراجات عبر التدريب والدعم والحوافز",
      "نشر محتوى فني وتجارب عملية توضح الفرق في الأداء",
    ],
    marketingMessage: "الجودة الألمانية، حماية المحرك، صيانة وقائية، حلول احترافية للورش، قيمة مرتفعة مقابل السعر",
  },
  {
    name: "TUNAP",
    country: "ألمانيا",
    foundedYear: 1972,
    localDistributor: null,
    tier: 1,
    pricingTier: "premium",
    threatRating: 5,
    productCategories: [
      "Petrol Injector Cleaner", "Diesel Injector Cleaner", "Fuel System Cleaner",
      "Engine Flush", "Oil System Cleaner", "Oil Additives", "DPF Cleaner",
      "EGR Cleaner", "Intake Cleaner", "Turbo Cleaning Products",
      "Cooling System Products", "Air Conditioning Service Products",
    ],
    strengths: [
      "علامة ألمانية متخصصة بالكامل في كيميائيات السيارات",
      "جودة عالية جدًا",
      "منتجات متقدمة للمحركات الحديثة",
      "سمعة ممتازة لدى الفنيين",
      "تعتمدها العديد من الوكالات ومراكز الخدمة عالميًا",
    ],
    weaknesses: [
      "لا يوجد وكيل رسمي في الضفة الغربية",
      "توفر المنتجات يعتمد على الاستيراد الموازي",
      "انتشار محدود مقارنة بالعلامات ذات الوكلاء الرسميين",
      "دعم تسويقي محلي ضعيف",
    ],
    swot: {
      s: "جودة ألمانية، حلول تقنية متقدمة، ثقة الورش، محفظة منتجات واسعة.",
      w: "غياب وكيل رسمي، انتشار محدود، اعتماد على الاستيراد الموازي.",
      o: "زيادة الطلب على المنتجات الاحترافية مع تطور السيارات الحديثة.",
      t: "المنافسة من JLM وBG وLiqui Moly وWynn's، وعدم استقرار التوريد المحلي.",
    },
    tows: {
      so: "استغلال السمعة الفنية للتوسع في الكراجات المتخصصة.",
      wo: "بناء شبكة توزيع مستقرة أو تعيين وكيل رسمي مستقبلًا.",
      st: "إبراز الحلول التقنية والاعتمادات الفنية لمواجهة المنافسين.",
      wt: "تقوية توفر المنتجات والدعم الفني لتقليل أثر غياب الوكيل.",
    },
    opportunitiesForJlm: [
      "الاستفادة من وجود وكيل رسمي لـ JLM وتوفير المنتجات باستمرار",
      "بناء برامج تدريب واعتماد للكراجات",
      "التركيز على خدمة ما بعد البيع والدعم الفني المحلي",
      "تنفيذ تجارب ميدانية ومقارنات أداء لإظهار القيمة العملية",
    ],
    marketingMessage:
      "التكنولوجيا الألمانية، حلول الصيانة الوقائية، زيادة عمر المحرك، التعاون مع الوكالات والـ OEMs، التدريب والدعم الفني للورش",
  },
  {
    name: "FLAMINGO",
    country: "أصل أمريكي — التصنيع والمبيعات العالمية حاليًا من الصين",
    foundedYear: null,
    localDistributor: "MP – Moving Parts (+ استيراد تجاري)",
    tier: 3,
    pricingTier: "value",
    threatRating: 3,
    productCategories: [
      "Fuel Injector Cleaner", "Diesel Injector Cleaner", "Fuel System Cleaner",
      "Engine Flush", "Oil Treatment", "Smoke Stop", "Octane Booster",
      "Catalytic Cleaner", "Power Steering Additives", "Cooling System Products",
    ],
    strengths: [
      "أسعار منافسة",
      "عدد كبير من الأصناف",
      "توفر جيد في السوق",
      "انتشار جيد بين الكراجات",
      "تغطي معظم فئات إضافات المحركات والعناية بالمركبات",
    ],
    weaknesses: [
      "ليست علامة Premium مثل JLM أو BG أو TUNAP",
      "الاعتماد الأساسي على ميزة السعر",
      "حضورها الفني والاحترافي أقل من المنافسين المتخصصين",
      "تفاوت صورة العلامة بين الأسواق المختلفة",
    ],
    swot: {
      s: "أسعار مناسبة، تشكيلة واسعة، انتشار جيد، توفر مستمر.",
      w: "تموضع اقتصادي أكثر من كونه احترافيًا، وقيمة العلامة أقل من المنافسين Premium.",
      o: "التوسع في شريحة الكراجات والعملاء الحساسين للسعر.",
      t: "المنافسة من JLM وLiqui Moly وWynn's وBG، إضافة إلى العلامات الاقتصادية الأخرى.",
    },
    tows: {
      so: "استغلال السعر والتنوع للتوسع في نقاط البيع والكراجات.",
      wo: "تحسين الصورة الفنية للعلامة عبر التدريب والتوعية.",
      st: "المحافظة على ميزة السعر مع تحسين جودة الرسائل التسويقية.",
      wt: "بناء ولاء لدى التجار والكراجات لتقليل أثر المنافسة من العلامات الأقوى.",
    },
    opportunitiesForJlm: [
      "التركيز على التخصص والجودة بدلًا من الدخول في منافسة سعرية",
      "إبراز الاعتمادات الفنية ونتائج الاختبارات العملية",
      "تقديم تدريب للكراجات لإظهار الفارق في الأداء",
      "التركيز على المنتجات المتخصصة (DPF، EGR، Turbo، GDI)",
    ],
    marketingMessage:
      "القيمة مقابل السعر، تشكيلة كبيرة من منتجات العناية والإضافات، سهولة الاستخدام، تحسين أداء المركبة بتكلفة منخفضة",
  },
  {
    name: "K2",
    country: "بولندا",
    foundedYear: 1991,
    localDistributor: null,
    tier: 3,
    pricingTier: "value",
    threatRating: 3,
    productCategories: [
      "Petrol Injector Cleaner", "Diesel Injector Cleaner", "Fuel System Cleaner",
      "Engine Flush", "Oil Additives", "DPF Cleaner", "Radiator Flush / Stop Leak",
      "Cooling System Products", "Engine Treatments",
    ],
    strengths: [
      "علامة أوروبية معروفة",
      "تشكيلة ضخمة جدًا من المنتجات",
      "أسعار مناسبة",
      "انتشار جيد في متاجر العناية بالمركبات",
      "توفر جيد في البيع الإلكتروني",
    ],
    weaknesses: [
      "ليست متخصصة في إضافات المحركات فقط",
      "حضورها في الكراجات المتخصصة أقل من BG أو TUNAP أو JLM",
      "عدم وجود وكيل رسمي مؤكد في الضفة",
    ],
    swot: {
      s: "تنوع كبير، أسعار مناسبة، انتشار جيد في قنوات البيع بالتجزئة.",
      w: "تركيز أقل على الإضافات الاحترافية، وعدم وجود وكيل رسمي مؤكد.",
      o: "نمو سوق العناية بالمركبات والبيع الإلكتروني.",
      t: "المنافسة من JLM وLiqui Moly وWynn's والعلامات الاقتصادية الأخرى.",
    },
    tows: {
      so: "استغلال تنوع المنتجات والتواجد في متاجر الكماليات لزيادة الحصة السوقية.",
      wo: "تعزيز الحضور الفني في الكراجات المتخصصة.",
      st: "المحافظة على ميزة السعر والتنوع لمواجهة المنافسين الأعلى سعرًا.",
      wt: "تحسين قنوات التوزيع والدعم الفني إذا تم تعيين وكيل رسمي مستقبلًا.",
    },
    opportunitiesForJlm: [
      "التركيز على أن JLM علامة متخصصة بالكامل في إضافات المحركات",
      "إبراز النتائج الفنية والاختبارات مقارنة بالعلامات العامة",
      "بناء شراكات مع الكراجات بدلًا من الاعتماد على متاجر الكماليات",
      "تعزيز التدريب الفني والدعم بعد البيع",
    ],
    marketingMessage: "الجودة الأوروبية، القيمة مقابل السعر، تنوع المنتجات، حلول متكاملة للعناية بالمركبة والمحرك",
  },
  {
    name: "German Adler",
    country: "ألمانيا (فرانكفورت)",
    foundedYear: null,
    localDistributor: null,
    tier: 3,
    pricingTier: "value",
    threatRating: 3,
    productCategories: [
      "Petrol Injection Cleaner", "Diesel System Cleaner", "Engine Flush",
      "Oil Treatment", "DPF Cleaner", "Catalyst Cleaner", "Radiator Cleaner",
      "Radiator Leak Stop", "Anti Smoke", "Octane Booster", "Cetane Booster",
    ],
    strengths: [
      "علامة ألمانية",
      "مجموعة واسعة من الإضافات والزيوت",
      "أسعار تنافسية",
      "تغطي معظم احتياجات الكراجات",
      "مناسبة للتجار الباحثين عن هامش ربح جيد",
    ],
    weaknesses: [
      "شهرة محدودة مقارنة بـ Liqui Moly وBG وWynn's",
      "عدم وجود وكيل رسمي في الضفة",
      "محدودية النشاط التسويقي المحلي",
      "الاعتماد على شبكة موزعين غير مركزية",
    ],
    swot: {
      s: "جودة ألمانية، تشكيلة واسعة، سعر مناسب.",
      w: "ضعف شهرة العلامة، غياب وكيل رسمي، تسويق محدود.",
      o: "استقطاب الكراجات التي تبحث عن جودة أوروبية بسعر اقتصادي.",
      t: "المنافسة من JLM وLiqui Moly وWynn's وPROFI-CAR، إضافة إلى العلامات الاقتصادية.",
    },
    tows: {
      so: "التوسع عبر شبكة تجار قطع الغيار والموزعين.",
      wo: "تعزيز الحضور التسويقي والدعم الفني في السوق الفلسطيني.",
      st: "استثمار ميزة صنع في ألمانيا مع الحفاظ على الأسعار التنافسية.",
      wt: "تحسين استقرار التوريد وبناء هوية أقوى للعلامة لدى الكراجات.",
    },
    opportunitiesForJlm: [
      "إبراز الاعتمادات الفنية والاختبارات العملية التي تتميز بها JLM",
      "التركيز على الحلول المتخصصة (DPF، GDI، Turbo، EGR)",
      "الاستفادة من وجود وكيل رسمي ودعم فني محلي",
      "بناء برامج ولاء وتدريب للكراجات",
    ],
    marketingMessage: "Made in Germany، الجودة الألمانية، الأداء العالي، مجموعة متكاملة من الزيوت والإضافات، أسعار منافسة",
  },
  {
    name: "American Eagle",
    country: "علامة أمريكية (تُنتج بعض خطوطها في دول مختلفة حسب الفئة)",
    foundedYear: null,
    localDistributor: null,
    tier: 4,
    pricingTier: "value",
    threatRating: 2,
    productCategories: [
      "Fuel Injector Cleaner", "Fuel System Cleaner", "Engine Flush", "Oil Treatment",
      "Diesel Additives", "Throttle Body Cleaner", "Carburetor Cleaner",
      "Brake Cleaner", "Contact Cleaner", "Silicone Spray", "Penetrating Oil",
    ],
    strengths: [
      "انتشار جيد في محلات الكماليات",
      "تشكيلة كبيرة من السبريهات الكيميائية",
      "أسعار مناسبة",
      "توفر جيد في السوق",
      "مقبولة لدى كثير من الكراجات",
    ],
    weaknesses: [
      "ليست علامة متخصصة في إضافات المحركات",
      "شهرتها في السبريهات أكبر من إضافات الوقود",
      "لا يوجد وكيل رسمي أو دعم فني محلي",
      "منافسة قوية من العلامات الاحترافية في مجال الإضافات",
    ],
    swot: {
      s: "انتشار جيد، أسعار مناسبة، تنوع كبير في السبريهات.",
      w: "ضعف التخصص في إضافات المحركات، وعدم وجود وكيل رسمي.",
      o: "الاستفادة من انتشار محلات الكماليات للوصول إلى المستهلك النهائي.",
      t: "المنافسة من العلامات المتخصصة مثل JLM وBG وWynn's وLiqui Moly.",
    },
    tows: {
      so: "استغلال الانتشار الواسع للسبريهات لزيادة بيع الإضافات.",
      wo: "تعزيز صورة العلامة في مجال إضافات المحركات.",
      st: "الحفاظ على الأسعار التنافسية مع تحسين جودة الرسائل التسويقية.",
      wt: "توسيع شبكة التوزيع والدعم الفني إذا تم تعيين موزع رسمي.",
    },
    opportunitiesForJlm: [
      "التأكيد على أن JLM متخصصة بالكامل في إضافات المحركات وليس فقط منتجات الصيانة العامة",
      "التركيز على الأداء والاعتمادات الفنية في المنتجات المتخصصة",
      "تعزيز العلاقة مع الكراجات عبر التدريب والدعم الفني",
      "تجنب المنافسة السعرية والتركيز على القيمة والنتائج",
    ],
    marketingMessage: "تعدد الاستخدامات، السعر المناسب، سهولة الاستخدام، حلول الصيانة اليومية",
  },
  {
    name: "BIZOL",
    country: "ألمانيا",
    foundedYear: 1998,
    localDistributor: "Moving Parts (MP) — فلسطين",
    tier: 2,
    pricingTier: "mid",
    threatRating: 4,
    productCategories: [
      "Petrol Injector Cleaner", "Diesel Injector Cleaner", "Fuel System Cleaner",
      "Engine Flush", "Oil Additives", "Oil System Cleaner", "DPF Cleaner",
      "Radiator Flush", "Radiator Stop Leak", "Transmission Additives",
      "Engine Protection Additives",
    ],
    strengths: [
      "علامة ألمانية متخصصة",
      "مجموعة واسعة من الإضافات والزيوت",
      "وكيل محلي نشط",
      "جودة جيدة واعتمادات أوروبية",
      "تغطية جيدة لاحتياجات الكراجات",
    ],
    weaknesses: [
      "شهرة أقل من Liqui Moly وWynn's",
      "حضور رقمي وتسويقي محدود نسبيًا في السوق الفلسطيني",
      "صورة العلامة لدى المستهلك النهائي ما زالت أقل من بعض المنافسين",
    ],
    swot: {
      s: "جودة ألمانية، وكيل محلي، تشكيلة متكاملة، صورة احترافية.",
      w: "شهرة أقل من كبار المنافسين، اعتماد على الوكيل في بناء العلامة.",
      o: "التوسع في الكراجات المستقلة وزيادة الطلب على الصيانة الوقائية.",
      t: "المنافسة من JLM وLiqui Moly وWynn's وBG وTUNAP.",
    },
    tows: {
      so: "استغلال قوة الوكيل والتكنولوجيا الألمانية للتوسع في السوق.",
      wo: "زيادة الاستثمار في التسويق الفني والتوعية بالعلامة.",
      st: "التركيز على الجودة والاعتمادات الأوروبية لمواجهة المنافسين.",
      wt: "تعزيز ولاء الكراجات عبر التدريب والدعم الفني.",
    },
    opportunitiesForJlm: [
      "إبراز أن JLM متخصصة بالكامل في إضافات المحركات، بينما BIZOL معروفة أيضًا بقوة في الزيوت",
      "التركيز على المنتجات المتخصصة مثل DPF وGDI وTurbo وتنظيف أنظمة الوقود",
      "تقديم برامج تدريب للكراجات لإظهار الفروق العملية في الأداء",
      "بناء ولاء طويل الأمد مع الكراجات عبر الدعم الفني والمتابعة",
    ],
    marketingMessage: "التكنولوجيا الألمانية، حماية المحرك، الصيانة الوقائية، تحسين الأداء، الالتزام بالمواصفات والاعتمادات الأوروبية",
  },
  {
    name: "AVANTOL",
    country: "ألمانيا",
    foundedYear: null,
    localDistributor: "شركة الحواري التجارية",
    tier: 2,
    pricingTier: "mid",
    threatRating: 4,
    productCategories: [
      "Petrol Injector Cleaner", "Diesel Injector Cleaner", "Fuel System Cleaner",
      "Engine Flush", "Oil Additives", "Engine Treatment", "Radiator Products",
      "Transmission Fluids & Additives", "Cooling System Products",
    ],
    strengths: [
      "علامة ألمانية",
      "وكيل محلي نشط",
      "شبكة توزيع جيدة",
      "أسعار تنافسية",
      "تكامل بين الزيوت والإضافات",
    ],
    weaknesses: [
      "شهرة أقل من Liqui Moly وWynn's",
      "التركيز التسويقي الأكبر على الزيوت أكثر من الإضافات",
      "الاعتماد على قوة الوكيل لبناء العلامة في السوق",
    ],
    swot: {
      s: "جودة ألمانية، وكيل قوي، انتشار جيد، تكامل المنتجات.",
      w: "حضور الإضافات أقل من حضور الزيوت، شهرة محدودة مقارنة بالعلامات العالمية الكبرى.",
      o: "التوسع في بيع الإضافات عبر شبكة الحواري الحالية.",
      t: "المنافسة من JLM وLiqui Moly وBIZOL وPROFI-CAR وWynn's.",
    },
    tows: {
      so: "استغلال شبكة الحواري للتوسع في بيع الإضافات مع الزيوت.",
      wo: "زيادة التسويق الفني لفئة الإضافات وليس الزيوت فقط.",
      st: "إبراز الجودة الألمانية والسعر المناسب لمواجهة المنافسين الأوروبيين.",
      wt: "تعزيز التدريب والدعم الفني للكراجات لرفع الوعي بالمنتجات.",
    },
    opportunitiesForJlm: [
      "التأكيد على أن JLM متخصصة بالكامل في إضافات المحركات، بينما Avantol تُعرف أكثر في سوق الزيوت",
      "التركيز على المنتجات المتقدمة مثل DPF وGDI وEGR وTurbo",
      "تقديم تدريب واعتمادات فنية للكراجات لزيادة الولاء",
      "إبراز نتائج الاختبارات والأداء العملي لمنتجات JLM",
    ],
    marketingMessage: "الجودة الألمانية، حماية المحرك، إطالة عمر المحرك، الأداء في الظروف القاسية، الاعتماد على شبكة موزعين محلية قوية",
  },
  {
    name: "LUBEGARD",
    country: "الولايات المتحدة الأمريكية",
    foundedYear: null,
    localDistributor: "شركة الحواري التجارية",
    tier: 5,
    pricingTier: "premium",
    threatRating: 3,
    productCategories: [
      "Automatic Transmission Additives", "CVT Additives", "Instant Shudder Fix",
      "Transmission Protectants", "Power Steering Fluids / Additives",
      // ملاحظة: لا يوفر — Engine Fuel Additives, Injector Cleaners, Engine Flush, DPF/EGR Products
    ],
    strengths: [
      "علامة متخصصة جدًا في إضافات ناقل الحركة",
      "سمعة ممتازة بين ورش الجير الأوتوماتيك",
      "وكيل رسمي نشط",
      "منتجات ذات أداء مثبت في هذا المجال",
    ],
    weaknesses: [
      "لا تغطي معظم فئات إضافات المحركات",
      "قاعدة العملاء أضيق من العلامات متعددة المنتجات",
      "الاعتماد على سوق متخصص",
    ],
    swot: {
      s: "تخصص واضح، جودة عالية، وكيل رسمي، ثقة لدى الفنيين.",
      w: "لا ينافس في معظم فئات إضافات المحركات.",
      o: "نمو الطلب على صيانة نواقل الحركة الحديثة (AT، CVT، DCT).",
      t: "المنافسة من JLM وLiqui Moly وWynn's وBG في فئة إضافات ناقل الحركة.",
    },
    tows: {
      so: "التوسع عبر ورش الجير المتخصصة.",
      wo: "إضافة منتجات جديدة لتوسيع قاعدة العملاء.",
      st: "إبراز التخصص والنتائج العملية في إصلاح مشاكل ناقل الحركة.",
      wt: "الحفاظ على التوفر والدعم الفني لمواجهة المنافسين متعددي الفئات.",
    },
    opportunitiesForJlm: [
      "المنافسة في باقي فئات إضافات المحركات حيث لا يتواجد LUBEGARD",
      "إبراز تنوع محفظة JLM مقارنة بتخصص LUBEGARD",
      "تقديم حلول متكاملة للمحرك وناقل الحركة ضمن علامة واحدة",
      "دعم الكراجات بالتدريب على الاستخدام الصحيح للإضافات",
    ],
    marketingMessage: "إطالة عمر ناقل الحركة، تقليل الاهتزاز (Shudder)، تحسين نعومة تبديل السرعات، تجنب الإصلاحات المكلفة",
  },
];

// Sourced from "JLM Lubricants.docx" (تحليل هوية العلامة التجارية).
const JLM_BRAND_ANALYSIS = `
نبذة عن العلامة: JLM Lubricants — مجال مواد كيميائية وإضافات السيارات (Automotive Chemicals & Additives).
الانطباع الأول: احترافية، جودة أوروبية، تركيز على الأداء والاعتمادية أكثر من الجانب العاطفي.

الشعار: تصميم بسيط (Minimal)، خطوط Sans Serif حديثة، رمز دائري يوحي بالحركة والمحرك والميكانيكا والدقة.
نقاط قوة الشعار: سهل التذكر، قابل للطباعة على العبوات، واضح بأحجام مختلفة.

لوحة الألوان الرسمية:
- الأصفر: الطاقة، القوة، النشاط، لفت الانتباه، الصناعة — لون مشهور في قطاع السيارات.
- الأسود: الاحترافية، القوة، الجودة، الفخامة.
- الأبيض: التوازن والوضوح.
- الأحمر: يظهر في أغطية العبوات — الأداء، القوة، التحذير، السرعة.

الخطوط: تعطي انطباعًا بالحداثة، التقنية، الوضوح، وسهولة القراءة.

أسلوب الصور: صور منتجات حقيقية، خلفيات صناعية، بيئة ورش وسيارات، إضاءة منخفضة، ألوان داكنة — الهدف خلق شعور بالقوة والخبرة الفنية.

شخصية العلامة: احترافية، تقنية، قوية، موثوقة، عملية، خبيرة، دقيقة — لا تعتمد على الطابع المرح أو العاطفي.

تموضع العلامة: حلول احترافية لتحسين أداء السيارة وإطالة عمرها — وليست مجرد شركة تبيع إضافات للمحركات.

الرسالة التسويقية (الشعار الظاهر): "We Understand Cars" — نحن خبراء، نفهم السيارات، منتجاتنا مبنية على خبرة تقنية. يعزز هذا الثقة أكثر من التركيز على السعر.

الجمهور المستهدف: أصحاب السيارات، ورش الصيانة، الميكانيكيون، موزعو الزيوت والإضافات، مراكز الخدمة، عشاق السيارات.

هوية المنتج (التغليف): لون لكل فئة، كتابة واضحة، شعار كبير، تصميم نظيف، معلومات تقنية — يسهل تمييز المنتجات على الرفوف.

أسلوب التواصل (Tone of Voice): احترافي، مباشر، تقني، يعتمد على الحقائق، يبني الثقة — لا يستخدم لغة دعائية مبالغًا فيها.

نقاط القوة في الهوية: هوية بصرية متسقة، ألوان مميزة يسهل تذكرها، شعار بسيط وقوي، تركيز واضح على الجودة، تغليف احترافي، سهولة التعرف على العلامة.

نقاط يمكن تطويرها: زيادة إبراز قصص النجاح وشهادات العملاء، استخدام عناصر بصرية أكثر لإظهار نتائج الاستخدام (قبل/بعد).

ملاحظة توزيع: يوجد منتجات على موقع JLM أكثر من المنتجات الموجودة على موقع UMT (ليست كل المنتجات متوفرة لدى المتحدة للسيارات)، لكن يمكن شحنها لعملاء B2B. المنتجات الموجودة على موقع UMT يمكن العمل عليها كـ B2B وB2C معًا.
`.trim();

async function seedOwner() {
  const email = process.env.SEED_OWNER_EMAIL ?? "owner@jlm.local";
  const password = process.env.SEED_OWNER_PASSWORD ?? "changeme123";
  const passwordHash = await bcrypt.hash(password, 10);

  const user = await prisma.user.upsert({
    where: { email },
    update: { passwordHash },
    create: { email, name: "مدير المنصة", passwordHash, role: "owner" },
  });

  console.log(`Seeded owner user: ${user.email} (password: ${password})`);
}

async function seedCompetitors() {
  for (const c of COMPETITORS) {
    await prisma.competitor.upsert({
      where: { name: c.name },
      update: {
        country: c.country,
        foundedYear: c.foundedYear,
        localDistributor: c.localDistributor,
        tier: c.tier,
        pricingTier: c.pricingTier,
        threatRating: c.threatRating,
        productCategories: c.productCategories as Prisma.InputJsonValue,
        strengths: c.strengths as Prisma.InputJsonValue,
        weaknesses: c.weaknesses as Prisma.InputJsonValue,
        swot: c.swot as Prisma.InputJsonValue,
        tows: c.tows as Prisma.InputJsonValue,
        opportunitiesForJlm: c.opportunitiesForJlm as Prisma.InputJsonValue,
        marketingMessage: c.marketingMessage,
      },
      create: {
        name: c.name,
        country: c.country,
        foundedYear: c.foundedYear,
        localDistributor: c.localDistributor,
        tier: c.tier,
        pricingTier: c.pricingTier,
        threatRating: c.threatRating,
        productCategories: c.productCategories as Prisma.InputJsonValue,
        strengths: c.strengths as Prisma.InputJsonValue,
        weaknesses: c.weaknesses as Prisma.InputJsonValue,
        swot: c.swot as Prisma.InputJsonValue,
        tows: c.tows as Prisma.InputJsonValue,
        opportunitiesForJlm: c.opportunitiesForJlm as Prisma.InputJsonValue,
        marketingMessage: c.marketingMessage,
      },
    });
  }
  console.log(`Seeded ${COMPETITORS.length} competitors.`);
}

async function seedKnowledgeFiles() {
  await prisma.knowledgeFile.upsert({
    where: { id: "seed-competitor-analysis" },
    update: { status: "processed" },
    create: {
      id: "seed-competitor-analysis",
      title: "COMPETITOR ANALYSIS (JLM).docx",
      category: "competitor",
      status: "processed",
      extractedText:
        "تم استخلاص بيانات 17 منافسًا (الملف التعريفي، SWOT، TOWS، مستوى التهديد، الفرص) وتحميلها مباشرة إلى جدول Competitor.",
    },
  });

  await prisma.knowledgeFile.upsert({
    where: { id: "seed-jlm-lubricants-brand" },
    update: { status: "processed", extractedText: JLM_BRAND_ANALYSIS },
    create: {
      id: "seed-jlm-lubricants-brand",
      title: "JLM Lubricants.docx (تحليل الهوية البصرية)",
      category: "company",
      status: "processed",
      extractedText: JLM_BRAND_ANALYSIS,
    },
  });

  await prisma.knowledgeFile.upsert({
    where: { id: "seed-product-catalogue" },
    update: { fileUrl: "/uploads/jlm-catalogue.pdf" },
    create: {
      id: "seed-product-catalogue",
      title: "JLM_Catalogue_Arabic_2026_5.pdf",
      category: "catalogue",
      status: "pending",
      fileUrl: "/uploads/jlm-catalogue.pdf",
      extractedText:
        "كتالوج من 341 صفحة، أغلبها صور وليست نصًا قابلاً للاستخراج المباشر. " +
        "بحاجة لخط استخراج بصري (vision-based) لقراءة كل صفحة كصورة واستخلاص بيانات المنتجات " +
        "(الاسم، SKU، الحجم، السعر، الوصف) بدقة — هذا مخطط له في مرحلة قاعدة المعرفة القادمة، " +
        "ولم يتم بعد إدخال أي منتج آليًا لتفادي أي ربط غير دقيق بين الأسماء والأسعار ورموز SKU.",
    },
  });

  console.log("Seeded knowledge base file records.");
}

// Colors are PLACEHOLDER hex values inferred from the written brand analysis
// (see JLM_BRAND_ANALYSIS above) — replace with exact codes once real brand
// assets are available; this page is meant to become their source of truth.
const BRAND_ASSETS: { type: string; label: string; value: string; notes?: string }[] = [
  {
    type: "color",
    label: "الأصفر (اللون الأساسي)",
    value: "#F5B301",
    notes: "الطاقة، القوة، النشاط، لفت الانتباه، الصناعة — لون مشهور في قطاع السيارات. قيمة مبدئية بانتظار الكود الرسمي.",
  },
  {
    type: "color",
    label: "الأسود",
    value: "#171310",
    notes: "الاحترافية، القوة، الجودة، الفخامة. قيمة مبدئية بانتظار الكود الرسمي.",
  },
  {
    type: "color",
    label: "الأبيض",
    value: "#FFFFFF",
    notes: "التوازن والوضوح.",
  },
  {
    type: "color",
    label: "الأحمر (على الأغطية)",
    value: "#D92D20",
    notes: "الأداء، القوة، التحذير، السرعة — يُستخدم بحذر كلون ثانوي فقط. قيمة مبدئية بانتظار الكود الرسمي.",
  },
  {
    type: "note",
    label: "الشعار التسويقي",
    value: "We Understand Cars",
    notes: "نحن خبراء، نفهم السيارات، منتجاتنا مبنية على خبرة تقنية — يعزز الثقة أكثر من التركيز على السعر.",
  },
  {
    type: "note",
    label: "شخصية العلامة",
    value: "احترافية، تقنية، قوية، موثوقة، عملية، خبيرة، دقيقة",
    notes: "لا تعتمد على الطابع المرح أو العاطفي.",
  },
  {
    type: "note",
    label: "الجمهور المستهدف",
    value: "أصحاب السيارات، ورش الصيانة، الميكانيكيون، موزعو الزيوت والإضافات، مراكز الخدمة، عشاق السيارات",
  },
  {
    type: "note",
    label: "أسلوب التواصل",
    value: "احترافي، مباشر، تقني، يعتمد على الحقائق، يبني الثقة — بدون لغة دعائية مبالغ فيها",
  },
];

async function seedBrandAssets() {
  for (const asset of BRAND_ASSETS) {
    const existing = await prisma.brandAsset.findFirst({ where: { label: asset.label } });
    if (existing) {
      await prisma.brandAsset.update({ where: { id: existing.id }, data: asset });
    } else {
      await prisma.brandAsset.create({ data: asset });
    }
  }
  console.log(`Seeded ${BRAND_ASSETS.length} brand assets.`);
}

const PROMPT_TEMPLATES: { title: string; mode: string; prompt: string }[] = [
  {
    title: "منشور تعليمي عن منتج",
    mode: "content",
    prompt: "اكتب منشور فيسبوك تعليمي يشرح مشكلة شائعة يحلها [اسم المنتج]، بدون أسلوب بيعي مباشر.",
  },
  {
    title: "Reel مقارنة قبل/بعد",
    mode: "reel",
    prompt: "ابنِ سكربت Reel مدته 30 ثانية يوضح الفرق قبل وبعد استخدام [اسم المنتج] على [نوع المشكلة].",
  },
  {
    title: "تحليل منافس سريع",
    mode: "competitor",
    prompt: "قارن بين JLM و[اسم المنافس] في فئة [الفئة]، وأبرز نقاط تفوق JLM بالاعتماد على قاعدة المعرفة فقط.",
  },
  {
    title: "خطة محتوى شهرية",
    mode: "monthly-plan",
    prompt: "ابنِ خطة محتوى لشهر [الشهر] لمنصات [فيسبوك/إنستغرام/تيك توك]، مع الالتزام بنسب المحتوى الافتراضية.",
  },
  {
    title: "تقييم حملة قبل الإطلاق",
    mode: "critic",
    prompt: "قيّم هذه الحملة قبل إطلاقها من حيث الوضوح، الإقناع، وملاءمتها للسوق الفلسطيني: [الصق تفاصيل الحملة]",
  },
  {
    title: "رد واتساب على استفسار سعر",
    mode: "whatsapp",
    prompt: "اكتب ردًا احترافيًا لعميل سأل عن سعر [اسم المنتج] ومدى توفره، مع دعوة لطيفة لإتمام الطلب.",
  },
];

async function seedPromptTemplates() {
  const count = await prisma.promptTemplate.count();
  if (count > 0) return;
  await prisma.promptTemplate.createMany({ data: PROMPT_TEMPLATES });
  console.log(`Seeded ${PROMPT_TEMPLATES.length} prompt templates.`);
}

async function main() {
  await seedOwner();
  await seedCompetitors();
  await seedKnowledgeFiles();
  await seedBrandAssets();
  await seedPromptTemplates();
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => process.exit(0));
