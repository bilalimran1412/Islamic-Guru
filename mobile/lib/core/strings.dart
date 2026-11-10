import 'app_language.dart';

/// UI strings for English, Urdu and Roman Urdu.
///
/// Kept as a simple map for the MVP because Roman Urdu is not a standard
/// locale. Move to ARB files when Arabic UI is added in Phase 2.
class S {
  S(this.lang);
  final AppLanguage lang;

  String _t(String en, String ur, String roman) => switch (lang) {
        AppLanguage.en => en,
        AppLanguage.ur => ur,
        AppLanguage.romanUr => roman,
      };

  String get appName => _t('Islamic Guru', 'اسلامک گرو', 'Islamic Guru');
  String get askHint => _t('Ask a question about Islam…', 'اسلام کے بارے میں سوال پوچھیں…',
      'Islam ke baare mein sawal poochein…');
  String get welcomeTitle => _t('Assalamu alaikum', 'السلام علیکم', 'Assalamu alaikum');
  String get welcomeBody => _t(
        'Ask any everyday question. Every answer comes from the Quran and Sahih hadith, with references you can open.',
        'روزمرہ زندگی کا کوئی بھی سوال پوچھیں۔ ہر جواب قرآن اور صحیح احادیث سے، حوالوں کے ساتھ دیا جاتا ہے۔',
        'Rozmarra zindagi ka koi bhi sawal poochein. Har jawab Quran aur Sahih ahadith se, hawalon ke saath diya jata hai.',
      );
  String get newChat => _t('New chat', 'نئی گفتگو', 'Nayi guftagu');
  String get history => _t('History', 'پچھلی گفتگو', 'Pichli guftagu');
  String get settings => _t('Settings', 'ترتیبات', 'Settings');
  String get language => _t('Language', 'زبان', 'Zaban');
  String get about => _t('About', 'تعارف', 'Taaruf');
  String get consultScholar => _t('Please also consult a qualified scholar on this.',
      'اس معاملے میں کسی مستند عالم سے بھی رجوع کریں۔', 'Is maamle mein kisi mustanad aalim se bhi rujoo karein.');
  String get report => _t('Report a problem', 'غلطی کی اطلاع دیں', 'Ghalti ki ittila dein');
  String get reportThanks => _t('Thank you. Our scholars will review this answer.',
      'شکریہ۔ ہمارے علماء اس جواب کا جائزہ لیں گے۔', 'Shukriya. Hamare ulama is jawab ka jaiza lenge.');
  String get wrongReference => _t('Wrong reference', 'غلط حوالہ', 'Ghalat hawala');
  String get wrongAnswer => _t('Wrong answer', 'غلط جواب', 'Ghalat jawab');
  String get sectarian => _t('Biased or sectarian', 'مسلکی تعصب', 'Maslaki taassub');
  String get other => _t('Other', 'دیگر', 'Deegar');
  String get send => _t('Send', 'بھیجیں', 'Bhejein');
  String get cancel => _t('Cancel', 'منسوخ', 'Mansookh');
  String get errorGeneric => _t('Something went wrong. Please try again.',
      'کچھ غلط ہو گیا۔ دوبارہ کوشش کریں۔', 'Kuch ghalat ho gaya. Dobara koshish karein.');
  String get dailyLimit => _t("You've reached today's free question limit.",
      'آج کے مفت سوالات کی حد پوری ہو گئی ہے۔', 'Aaj ke muft sawalat ki had poori ho gayi hai.');
  String get thinking => _t('Searching the Quran and hadith…', 'قرآن و حدیث میں تلاش جاری ہے…',
      'Quran o hadith mein talaash jari hai…');
  String get noHistory => _t('No conversations yet.', 'ابھی کوئی گفتگو نہیں۔', 'Abhi koi guftagu nahi.');
  String get translation => _t('Translation', 'ترجمہ', 'Tarjuma');
  String get grade => _t('Grade', 'درجہ', 'Darja');
  String get openSource => _t('Open source page', 'اصل ماخذ دیکھیں', 'Asal maakhaz dekhein');
  String get aboutBody => _t(
        'Islamic Guru answers questions using only the Quran and Sahih hadith (Sahih al-Bukhari and Sahih Muslim). '
            'It covers Sunni guidance from all four schools: Hanafi, Shafi\'i, Maliki and Hanbali. It does not cover Shia fiqh. '
            'Answers are guidance based on sources, not fatwas. If our library has no reliable answer, the app says so.',
        'اسلامک گرو صرف قرآن اور صحیح احادیث (صحیح بخاری اور صحیح مسلم) سے جواب دیتا ہے۔ یہ چاروں سنی مکاتبِ فکر — حنفی، شافعی، مالکی اور حنبلی — کی رہنمائی پر مشتمل ہے۔ اس میں شیعہ فقہ شامل نہیں۔ جوابات ماخذ پر مبنی رہنمائی ہیں، فتویٰ نہیں۔',
        'Islamic Guru sirf Quran aur Sahih ahadith (Sahih Bukhari aur Sahih Muslim) se jawab deta hai. Yeh charon Sunni makatib-e-fikr — Hanafi, Shafi\'i, Maliki aur Hanbali — ki rehnumai par mushtamil hai. Is mein Shia fiqh shamil nahi. Jawabat hawalon par mabni rehnumai hain, fatwa nahi.',
      );
}
