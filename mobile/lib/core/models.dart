class Citation {
  Citation({required this.index, required this.refKey, required this.label, required this.kind, this.quote});

  final int index;
  final String refKey;
  final String label;
  final String kind;
  final String? quote;

  factory Citation.fromJson(Map<String, dynamic> j) => Citation(
        index: j['index'] as int,
        refKey: j['ref_key'] as String,
        label: j['label'] as String,
        kind: j['kind'] as String,
        quote: j['quote'] as String?,
      );
}

enum AnswerStatus { answered, noAnswer, outOfScope }

AnswerStatus _status(String? s) => switch (s) {
      'answered' => AnswerStatus.answered,
      'out_of_scope' => AnswerStatus.outOfScope,
      _ => AnswerStatus.noAnswer,
    };

class ChatMessage {
  ChatMessage({
    required this.role,
    required this.content,
    this.id,
    this.citations = const [],
    this.status,
    this.consultScholar = false,
    this.disclaimer,
    this.language,
  });

  final String? id;
  final String role; // 'user' | 'assistant'
  final String content;
  final List<Citation> citations;
  final AnswerStatus? status;
  final bool consultScholar;
  final String? disclaimer;
  final String? language;

  bool get isUser => role == 'user';

  /// From POST /v1/ask.
  factory ChatMessage.fromAsk(Map<String, dynamic> j) => ChatMessage(
        id: j['message_id'] as String,
        role: 'assistant',
        content: j['answer'] as String,
        citations: (j['citations'] as List).map((c) => Citation.fromJson(c as Map<String, dynamic>)).toList(),
        status: _status(j['status'] as String?),
        consultScholar: j['consult_scholar'] as bool? ?? false,
        disclaimer: j['disclaimer'] as String?,
        language: j['language'] as String?,
      );

  /// From GET /v1/chats/{id}.
  factory ChatMessage.fromHistory(Map<String, dynamic> j) {
    final meta = (j['meta'] as Map?)?.cast<String, dynamic>() ?? {};
    return ChatMessage(
      id: j['id'] as String,
      role: j['role'] as String,
      content: j['content'] as String,
      citations: ((meta['citations'] as List?) ?? [])
          .map((c) => Citation.fromJson(c as Map<String, dynamic>))
          .toList(),
      status: j['role'] == 'assistant' ? _status(meta['status'] as String?) : null,
      consultScholar: meta['consult_scholar'] as bool? ?? false,
      disclaimer: meta['disclaimer'] as String?,
      language: meta['language'] as String?,
    );
  }
}

class ChatSummary {
  ChatSummary({required this.id, required this.title, required this.createdAt});
  final String id;
  final String title;
  final DateTime createdAt;

  factory ChatSummary.fromJson(Map<String, dynamic> j) => ChatSummary(
        id: j['id'] as String,
        title: j['title'] as String,
        createdAt: DateTime.parse(j['created_at'] as String),
      );
}

class SourceText {
  SourceText({
    required this.refKey,
    required this.kind,
    required this.label,
    required this.arabic,
    required this.translations,
    required this.grade,
    required this.attribution,
    required this.sourceUrl,
  });

  final String refKey;
  final String kind;
  final String label;
  final String? arabic;
  final Map<String, ({String text, String? translator})> translations;
  final String? grade;
  final String attribution;
  final String? sourceUrl;

  factory SourceText.fromJson(Map<String, dynamic> j) {
    final raw = (j['translations'] as Map?)?.cast<String, dynamic>() ?? {};
    return SourceText(
      refKey: j['ref_key'] as String,
      kind: j['kind'] as String,
      label: j['label'] as String,
      arabic: j['arabic'] as String?,
      translations: raw.map((lang, v) => MapEntry(
            lang,
            v is Map
                ? (text: v['text'] as String, translator: v['translator'] as String?)
                : (text: v.toString(), translator: null),
          )),
      grade: j['grade'] as String?,
      attribution: j['attribution'] as String,
      sourceUrl: j['source_url'] as String?,
    );
  }
}

class Profile {
  Profile({
    required this.userId,
    required this.email,
    required this.displayName,
    required this.signedInWith,
    required this.madhhab,
    required this.premiumActive,
  });

  final String userId;
  final String? email;
  final String? displayName;
  final String? signedInWith; // 'google' | 'apple' | null for guests
  final String? madhhab;
  final bool premiumActive;

  bool get isGuest => signedInWith == null;

  factory Profile.fromJson(Map<String, dynamic> j) => Profile(
        userId: j['user_id'] as String,
        email: j['email'] as String?,
        displayName: j['display_name'] as String?,
        signedInWith: j['signed_in_with'] as String?,
        madhhab: j['madhhab'] as String?,
        premiumActive: j['premium_active'] as bool? ?? false,
      );
}

class FatwaSummary {
  FatwaSummary({
    required this.id,
    required this.title,
    required this.publisher,
    required this.scholar,
    required this.madhhab,
    required this.language,
  });

  final String id;
  final String title;
  final String publisher;
  final String? scholar;
  final String? madhhab;
  final String language;

  factory FatwaSummary.fromJson(Map<String, dynamic> j) => FatwaSummary(
        id: j['id'] as String,
        title: j['title'] as String,
        publisher: j['publisher'] as String,
        scholar: j['scholar'] as String?,
        madhhab: j['madhhab'] as String?,
        language: j['language'] as String,
      );
}

class FatwaDetail extends FatwaSummary {
  FatwaDetail({
    required super.id,
    required super.title,
    required super.publisher,
    required super.scholar,
    required super.madhhab,
    required super.language,
    required this.question,
    required this.answer,
    required this.originalUrl,
  });

  final String? question;
  final String answer;
  final String originalUrl;

  factory FatwaDetail.fromJson(Map<String, dynamic> j) {
    final s = FatwaSummary.fromJson(j);
    return FatwaDetail(
      id: s.id,
      title: s.title,
      publisher: s.publisher,
      scholar: s.scholar,
      madhhab: s.madhhab,
      language: s.language,
      question: j['question'] as String?,
      answer: j['answer'] as String,
      originalUrl: j['original_url'] as String,
    );
  }
}

class ScholarQuestion {
  ScholarQuestion({
    required this.id,
    required this.question,
    required this.status,
    required this.answer,
    required this.scholarName,
    required this.createdAt,
  });

  final String id;
  final String question;
  final String status;
  final String? answer;
  final String? scholarName;
  final DateTime createdAt;

  factory ScholarQuestion.fromJson(Map<String, dynamic> j) => ScholarQuestion(
        id: j['id'] as String,
        question: j['question'] as String,
        status: j['status'] as String,
        answer: j['answer'] as String?,
        scholarName: j['scholar_name'] as String?,
        createdAt: DateTime.parse(j['created_at'] as String),
      );
}
