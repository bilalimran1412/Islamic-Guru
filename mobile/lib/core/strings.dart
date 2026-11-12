import 'app_language.dart';

/// UI strings for English, Urdu, Roman Urdu and Arabic.
///
/// A simple switch rather than ARB files because Roman Urdu is not a
/// standard locale.
class S {
  S(this.lang);
  final AppLanguage lang;

  String _t(String en, String ur, String roman, String ar) => switch (lang) {
        AppLanguage.en => en,
        AppLanguage.ur => ur,
        AppLanguage.romanUr => roman,
        AppLanguage.ar => ar,
      };

  // App and chat
  String get appName => _t('Islamic Guru', 'اسلامک گرو', 'Islamic Guru', 'المرشد الإسلامي');
  String get askHint => _t('Ask a question about Islam…', 'اسلام کے بارے میں سوال پوچھیں…',
      'Islam ke baare mein sawal poochein…', 'اسأل سؤالاً عن الإسلام…');
  String get welcomeTitle => _t('Assalamu alaikum', 'السلام علیکم', 'Assalamu alaikum', 'السلام عليكم');
  String get welcomeBody => _t(
        'Ask any everyday question. Every answer comes from the Quran and Sahih hadith, with references you can open.',
        'روزمرہ زندگی کا کوئی بھی سوال پوچھیں۔ ہر جواب قرآن اور صحیح احادیث سے، حوالوں کے ساتھ دیا جاتا ہے۔',
        'Rozmarra zindagi ka koi bhi sawal poochein. Har jawab Quran aur Sahih ahadith se, hawalon ke saath diya jata hai.',
        'اسأل أي سؤال من حياتك اليومية. كل إجابة من القرآن والأحاديث الصحيحة مع مراجع يمكنك فتحها.',
      );
  String get newChat => _t('New chat', 'نئی گفتگو', 'Nayi guftagu', 'محادثة جديدة');
  String get history => _t('History', 'پچھلی گفتگو', 'Pichli guftagu', 'السجل');
  String get settings => _t('Settings', 'ترتیبات', 'Settings', 'الإعدادات');
  String get language => _t('Language', 'زبان', 'Zaban', 'اللغة');
  String get about => _t('About', 'تعارف', 'Taaruf', 'حول التطبيق');
  String get consultScholar => _t('Please also consult a qualified scholar on this.',
      'اس معاملے میں کسی مستند عالم سے بھی رجوع کریں۔', 'Is maamle mein kisi mustanad aalim se bhi rujoo karein.',
      'يرجى أيضاً استشارة عالم مؤهل في هذه المسألة.');
  String get report => _t('Report a problem', 'غلطی کی اطلاع دیں', 'Ghalti ki ittila dein', 'الإبلاغ عن مشكلة');
  String get reportThanks => _t('Thank you. Our scholars will review this answer.',
      'شکریہ۔ ہمارے علماء اس جواب کا جائزہ لیں گے۔', 'Shukriya. Hamare ulama is jawab ka jaiza lenge.',
      'شكراً لك. سيراجع علماؤنا هذه الإجابة.');
  String get wrongReference => _t('Wrong reference', 'غلط حوالہ', 'Ghalat hawala', 'مرجع خاطئ');
  String get wrongAnswer => _t('Wrong answer', 'غلط جواب', 'Ghalat jawab', 'إجابة خاطئة');
  String get sectarian => _t('Biased or sectarian', 'مسلکی تعصب', 'Maslaki taassub', 'متحيز أو طائفي');
  String get other => _t('Other', 'دیگر', 'Deegar', 'أخرى');
  String get send => _t('Send', 'بھیجیں', 'Bhejein', 'إرسال');
  String get cancel => _t('Cancel', 'منسوخ', 'Mansookh', 'إلغاء');
  String get errorGeneric => _t('Something went wrong. Please try again.',
      'کچھ غلط ہو گیا۔ دوبارہ کوشش کریں۔', 'Kuch ghalat ho gaya. Dobara koshish karein.',
      'حدث خطأ ما. يرجى المحاولة مرة أخرى.');
  String get dailyLimit => _t("You've reached today's free question limit.",
      'آج کے مفت سوالات کی حد پوری ہو گئی ہے۔', 'Aaj ke muft sawalat ki had poori ho gayi hai.',
      'لقد وصلت إلى حد الأسئلة المجانية لهذا اليوم.');
  String get thinking => _t('Searching the Quran and hadith…', 'قرآن و حدیث میں تلاش جاری ہے…',
      'Quran o hadith mein talaash jari hai…', 'جارٍ البحث في القرآن والحديث…');
  String get noHistory => _t('No conversations yet.', 'ابھی کوئی گفتگو نہیں۔', 'Abhi koi guftagu nahi.',
      'لا توجد محادثات بعد.');
  String get translation => _t('Translation', 'ترجمہ', 'Tarjuma', 'الترجمة');
  String get grade => _t('Grade', 'درجہ', 'Darja', 'الدرجة');
  String get openSource => _t('Open source page', 'اصل ماخذ دیکھیں', 'Asal maakhaz dekhein', 'فتح المصدر');
  String get aboutBody => _t(
        'Islamic Guru answers questions using only the Quran, Sahih hadith (Sahih al-Bukhari and Sahih Muslim) and fatawa approved by our scholars. '
            'It covers Sunni guidance from all four schools: Hanafi, Shafi\'i, Maliki and Hanbali. It does not cover Shia fiqh. '
            'Answers are guidance based on sources, not fatwas. If our library has no reliable answer, the app says so.',
        'اسلامک گرو صرف قرآن، صحیح احادیث (صحیح بخاری اور صحیح مسلم) اور ہمارے علماء کے منظور شدہ فتاویٰ سے جواب دیتا ہے۔ یہ چاروں سنی مکاتبِ فکر — حنفی، شافعی، مالکی اور حنبلی — کی رہنمائی پر مشتمل ہے۔ اس میں شیعہ فقہ شامل نہیں۔ جوابات ماخذ پر مبنی رہنمائی ہیں، فتویٰ نہیں۔',
        'Islamic Guru sirf Quran, Sahih ahadith (Sahih Bukhari aur Sahih Muslim) aur hamare ulama ke manzoor shuda fatawa se jawab deta hai. Yeh charon Sunni makatib-e-fikr — Hanafi, Shafi\'i, Maliki aur Hanbali — ki rehnumai par mushtamil hai. Is mein Shia fiqh shamil nahi. Jawabat hawalon par mabni rehnumai hain, fatwa nahi.',
        'يجيب المرشد الإسلامي من القرآن والأحاديث الصحيحة (صحيح البخاري وصحيح مسلم) والفتاوى التي اعتمدها علماؤنا فقط. ويغطي إرشاد أهل السنة من المذاهب الأربعة: الحنفي والشافعي والمالكي والحنبلي، ولا يشمل الفقه الشيعي. الإجابات إرشاد مبني على المصادر وليست فتاوى.',
      );

  // Maslak
  String get maslak => _t('School of thought (maslak)', 'مسلک', 'Maslak', 'المذهب الفقهي');
  String get maslakHelp => _t(
        'Your school\'s view is shown first where scholars differ. Others are still shown.',
        'جہاں علماء کا اختلاف ہو وہاں آپ کے مسلک کی رائے پہلے دکھائی جائے گی، باقی آراء بھی ساتھ ہوں گی۔',
        'Jahan ulama ka ikhtilaf ho wahan aap ke maslak ki raye pehle dikhayi jayegi, baqi aara bhi saath hongi.',
        'حيث يختلف العلماء يُعرض رأي مذهبك أولاً، مع عرض الآراء الأخرى.',
      );
  String get allSchools => _t('All schools side by side', 'تمام مسالک ساتھ ساتھ', 'Tamam masalik saath saath',
      'جميع المذاهب جنباً إلى جنب');
  String madhhabName(String code) => switch (code) {
        'hanafi' => _t('Hanafi', 'حنفی', 'Hanafi', 'الحنفي'),
        'shafii' => _t("Shafi'i", 'شافعی', "Shafi'i", 'الشافعي'),
        'maliki' => _t('Maliki', 'مالکی', 'Maliki', 'المالكي'),
        'hanbali' => _t('Hanbali', 'حنبلی', 'Hanbali', 'الحنبلي'),
        'ahl_e_hadith' => _t('Ahl-e-Hadith', 'اہلِ حدیث', 'Ahl-e-Hadith', 'أهل الحديث'),
        _ => code,
      };

  // Account
  String get account => _t('Account', 'اکاؤنٹ', 'Account', 'الحساب');
  String get guestAccount => _t('Guest account: sign in to keep your history on all your devices.',
      'مہمان اکاؤنٹ: اپنی گفتگو ہر ڈیوائس پر محفوظ رکھنے کے لیے سائن اِن کریں۔',
      'Mehman account: apni guftagu har device par mehfooz rakhne ke liye sign in karein.',
      'حساب ضيف: سجّل الدخول للاحتفاظ بسجلك على جميع أجهزتك.');
  String get signedInAs => _t('Signed in as', 'سائن اِن', 'Sign in hain', 'تم تسجيل الدخول باسم');
  String get signInGoogle => _t('Sign in with Google', 'گوگل سے سائن اِن', 'Google se sign in', 'تسجيل الدخول عبر Google');
  String get signInApple => _t('Sign in with Apple', 'ایپل سے سائن اِن', 'Apple se sign in', 'تسجيل الدخول عبر Apple');
  String get signInFailed => _t('Sign-in did not complete.', 'سائن اِن مکمل نہیں ہوا۔', 'Sign in mukammal nahi hua.',
      'لم يكتمل تسجيل الدخول.');
  String get userId => _t('User ID', 'یوزر آئی ڈی', 'User ID', 'معرّف المستخدم');
  String get copied => _t('Copied', 'کاپی ہو گیا', 'Copy ho gaya', 'تم النسخ');
  String get premium => _t('Premium', 'پریمیم', 'Premium', 'بريميوم');
  String get premiumActive => _t('Premium is active: unlimited questions.', 'پریمیم فعال ہے: لامحدود سوالات۔',
      'Premium faal hai: la-mehdood sawalat.', 'البريميوم مفعّل: أسئلة غير محدودة.');
  String get premiumInfo => _t(
        'Free plan: a limited number of questions each day. Premium gives unlimited questions and priority for Ask a Scholar.',
        'مفت پلان: روزانہ محدود سوالات۔ پریمیم میں لامحدود سوالات اور "عالم سے پوچھیں" میں ترجیح۔',
        'Muft plan: rozana mehdood sawalat. Premium mein la-mehdood sawalat aur "Aalim se poochein" mein tarjeeh.',
        'الخطة المجانية: عدد محدود من الأسئلة يومياً. البريميوم: أسئلة غير محدودة وأولوية في "اسأل عالماً".',
      );

  // Fatawa library
  String get library => _t('Fatawa library', 'فتاویٰ لائبریری', 'Fatawa library', 'مكتبة الفتاوى');
  String get searchFatawa => _t('Search fatawa…', 'فتاویٰ تلاش کریں…', 'Fatawa talaash karein…', 'ابحث في الفتاوى…');
  String get noFatawa => _t('No fatawa found.', 'کوئی فتویٰ نہیں ملا۔', 'Koi fatwa nahi mila.', 'لم يتم العثور على فتاوى.');
  String get readOriginal => _t('Read the original', 'اصل فتویٰ پڑھیں', 'Asal fatwa parhein', 'اقرأ الأصل');
  String get question => _t('Question', 'سوال', 'Sawal', 'السؤال');
  String get answer => _t('Answer', 'جواب', 'Jawab', 'الجواب');

  // Ask a Scholar
  String get askScholar => _t('Ask a Scholar', 'عالم سے پوچھیں', 'Aalim se poochein', 'اسأل عالماً');
  String get askScholarIntro => _t(
        'For personal matters, send your question to our scholar panel. A scholar will answer you personally.',
        'ذاتی معاملات کے لیے اپنا سوال ہمارے علماء کو بھیجیں۔ ایک عالم آپ کو خود جواب دیں گے۔',
        'Zaati maamlaat ke liye apna sawal hamare ulama ko bhejein. Ek aalim aap ko khud jawab denge.',
        'للمسائل الشخصية أرسل سؤالك إلى لجنة العلماء، وسيجيبك أحد العلماء شخصياً.',
      );
  String get yourQuestion => _t('Your question', 'آپ کا سوال', 'Aap ka sawal', 'سؤالك');
  String get submit => _t('Submit', 'جمع کریں', 'Jama karein', 'إرسال');
  String get noScholarQuestions => _t('You have not asked a scholar yet.', 'آپ نے ابھی کسی عالم سے سوال نہیں پوچھا۔',
      'Aap ne abhi kisi aalim se sawal nahi poocha.', 'لم تسأل عالماً بعد.');
  String scholarStatus(String status) => switch (status) {
        'awaiting_payment' => _t('Awaiting payment', 'ادائیگی کا انتظار', 'Adaigi ka intezar', 'بانتظار الدفع'),
        'pending' => _t('Waiting for a scholar', 'عالم کے جواب کا انتظار', 'Aalim ke jawab ka intezar',
            'بانتظار العالم'),
        'answered' => _t('Answered', 'جواب آ گیا', 'Jawab aa gaya', 'تمت الإجابة'),
        'declined' => _t('Not answered', 'جواب نہیں دیا گیا', 'Jawab nahi diya gaya', 'لم تتم الإجابة'),
        _ => status,
      };
  String get paymentSoon => _t(
        'Payment for scholar questions will open with the app store release. Premium members can ask now.',
        'علماء کے سوالات کی ادائیگی ایپ اسٹور ریلیز کے ساتھ شروع ہوگی۔ پریمیم ممبرز ابھی پوچھ سکتے ہیں۔',
        'Ulama ke sawalat ki adaigi app store release ke saath shuru hogi. Premium members abhi pooch sakte hain.',
        'سيتوفر الدفع لأسئلة العلماء مع إصدار المتجر. يمكن لأعضاء البريميوم السؤال الآن.',
      );

  // Voice
  String get voice => _t('Speak your question', 'سوال بول کر پوچھیں', 'Sawal bol kar poochein', 'تحدث بسؤالك');
  String get listening => _t('Listening…', 'سن رہے ہیں…', 'Sun rahe hain…', 'جارٍ الاستماع…');
  String get voiceUnavailable => _t('Voice input is not available on this device.',
      'اس ڈیوائس پر آواز سے سوال کی سہولت دستیاب نہیں۔', 'Is device par awaz se sawal ki sahulat dastiyab nahi.',
      'الإدخال الصوتي غير متاح على هذا الجهاز.');
}
