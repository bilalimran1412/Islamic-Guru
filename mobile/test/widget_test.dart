import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:islamic_guru/core/api_client.dart';
import 'package:islamic_guru/core/app_language.dart';
import 'package:islamic_guru/core/strings.dart';
import 'package:islamic_guru/features/library/library_screen.dart';
import 'package:islamic_guru/features/scholar/scholar_screen.dart';
import 'package:islamic_guru/features/settings/settings_screen.dart';
import 'package:islamic_guru/core/models.dart';
import 'package:islamic_guru/features/chat/chat_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

class FakeApi extends ApiClient {
  String? lastLanguage;

  @override
  Future<({String chatId, ChatMessage answer})> ask(String question, {String? chatId, String? language}) async {
    lastLanguage = language;
    return (
      chatId: 'chat-1',
      answer: ChatMessage.fromAsk({
        'chat_id': 'chat-1',
        'message_id': 'msg-1',
        'status': 'answered',
        'language': 'en',
        'answer': 'Fasting in Ramadan is obligatory [1].',
        'citations': [
          {'index': 1, 'ref_key': 'quran:2:183', 'label': 'Surah Al-Baqarah 2:183', 'kind': 'quran', 'quote': null},
        ],
        'consult_scholar': false,
        'disclaimer': 'This is guidance based on sources, not a fatwa.',
      }),
    );
  }

  @override
  Future<List<ChatSummary>> chats() async => [];

  String? madhhabSet;

  @override
  Future<Profile> me() async => Profile(
        userId: 'user-1',
        email: null,
        displayName: null,
        signedInWith: null,
        madhhab: madhhabSet,
        premiumActive: false,
      );

  @override
  Future<Profile> updateMe({String? language, String? madhhab, bool clearMadhhab = false}) async {
    madhhabSet = clearMadhhab ? null : (madhhab ?? madhhabSet);
    return me();
  }

  @override
  Future<List<FatwaSummary>> fatwas({String? query, String? madhhab}) async => [
        FatwaSummary(id: 'f1', title: 'Zakat on gold', publisher: 'Test Darul Ifta', scholar: null,
            madhhab: 'hanafi', language: 'en'),
      ];

  @override
  Future<List<ScholarQuestion>> scholarQuestions() async => [
        ScholarQuestion(id: 'q1', question: 'A personal question', status: 'answered',
            answer: 'Wa alaikum assalam...', scholarName: 'Mufti Test', createdAt: DateTime(2026, 11, 12)),
      ];
}

Widget _app(FakeApi api, Widget home) => ProviderScope(
      overrides: [apiClientProvider.overrideWithValue(api)],
      child: MaterialApp(home: home),
    );

void main() {
  setUp(() => SharedPreferences.setMockInitialValues({}));

  testWidgets('asking a question shows the answer with its reference chip', (tester) async {
    final api = FakeApi();
    await tester.pumpWidget(ProviderScope(
      overrides: [apiClientProvider.overrideWithValue(api)],
      child: const MaterialApp(home: ChatScreen()),
    ));

    expect(find.text('Assalamu alaikum'), findsOneWidget);

    await tester.enterText(find.byType(TextField), 'Is fasting obligatory?');
    await tester.tap(find.byIcon(Icons.send));
    await tester.pumpAndSettle();

    expect(find.text('Is fasting obligatory?'), findsOneWidget);
    expect(find.text('Fasting in Ramadan is obligatory [1].'), findsOneWidget);
    expect(find.text('[1] Surah Al-Baqarah 2:183'), findsOneWidget);
    expect(find.text('Report a problem'), findsOneWidget);
    expect(api.lastLanguage, 'en');
  });

  testWidgets('choosing a maslak saves it to the account', (tester) async {
    final api = FakeApi();
    await tester.pumpWidget(_app(api, const SettingsScreen()));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(find.text('Hanafi'), 200);
    await tester.tap(find.text('Hanafi'));
    await tester.pumpAndSettle();
    expect(api.madhhabSet, 'hanafi');
  });

  testWidgets('fatawa library lists approved fatawa', (tester) async {
    await tester.pumpWidget(_app(FakeApi(), const LibraryScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Zakat on gold'), findsOneWidget);
    expect(find.text('Test Darul Ifta · Hanafi'), findsOneWidget);
  });

  testWidgets('Ask a Scholar shows answered questions', (tester) async {
    await tester.pumpWidget(_app(FakeApi(), const ScholarScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Mufti Test'), findsOneWidget);
    expect(find.text('Answered'), findsOneWidget);
  });

  test('every UI string exists in all four languages', () {
    for (final lang in AppLanguage.values) {
      final s = S(lang);
      for (final text in [s.appName, s.askHint, s.maslak, s.library, s.askScholar, s.voice, s.premiumInfo]) {
        expect(text, isNotEmpty, reason: '$lang');
      }
    }
    expect(S(AppLanguage.ar).appName, 'المرشد الإسلامي');
  });

  test('history messages parse citations from meta', () {
    final m = ChatMessage.fromHistory({
      'id': 'm1',
      'role': 'assistant',
      'content': 'Answer [1]',
      'meta': {
        'status': 'no_answer',
        'consult_scholar': true,
        'citations': [
          {'index': 1, 'ref_key': 'bukhari:1903', 'label': 'Sahih al-Bukhari 1903', 'kind': 'hadith'},
        ],
      },
      'created_at': '2026-11-10T10:00:00Z',
    });
    expect(m.status, AnswerStatus.noAnswer);
    expect(m.consultScholar, isTrue);
    expect(m.citations.single.refKey, 'bukhari:1903');
  });

  test('source text parses translator records', () {
    final src = SourceText.fromJson({
      'ref_key': 'quran:2:183',
      'kind': 'quran',
      'label': 'Surah Al-Baqarah 2:183',
      'arabic': 'يَا أَيُّهَا',
      'translations': {
        'en': {'text': 'O you who have believed', 'translator': 'Saheeh International'},
      },
      'grade': null,
      'attribution': 'Tanzil',
      'source_url': 'https://quran.com/2/183',
    });
    expect(src.translations['en']!.translator, 'Saheeh International');
  });
}
