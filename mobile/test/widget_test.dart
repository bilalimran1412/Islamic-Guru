import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:islamic_guru/core/api_client.dart';
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
}

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
