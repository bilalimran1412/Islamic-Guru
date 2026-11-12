import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'config.dart';
import 'models.dart';

class DailyLimitReached implements Exception {}

class ServiceUnavailable implements Exception {}

/// Talks to the FastAPI backend. Creates a guest account on first use and
/// keeps its token in secure storage.
class ApiClient {
  ApiClient({Dio? dio, FlutterSecureStorage? storage})
      : _dio = dio ?? Dio(BaseOptions(baseUrl: AppConfig.apiBaseUrl, receiveTimeout: const Duration(seconds: 90))),
        _storage = storage ?? const FlutterSecureStorage() {
    _dio.interceptors.add(InterceptorsWrapper(onRequest: (options, handler) async {
      if (!options.path.startsWith('/v1/auth')) {
        options.headers['Authorization'] = 'Bearer ${await _token()}';
      }
      handler.next(options);
    }));
  }

  static const _tokenKey = 'auth_token';
  final Dio _dio;
  final FlutterSecureStorage _storage;
  String? _cachedToken;

  Future<String> _token() async {
    _cachedToken ??= await _storage.read(key: _tokenKey);
    if (_cachedToken != null) return _cachedToken!;
    final res = await _dio.post<Map<String, dynamic>>('/v1/auth/guest');
    _cachedToken = res.data!['access_token'] as String;
    await _storage.write(key: _tokenKey, value: _cachedToken);
    return _cachedToken!;
  }

  Future<({String chatId, ChatMessage answer})> ask(String question, {String? chatId, String? language}) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>('/v1/ask', data: {
        'question': question,
        'chat_id': ?chatId,
        'language': ?language,
      });
      final data = res.data!;
      return (chatId: data['chat_id'] as String, answer: ChatMessage.fromAsk(data));
    } on DioException catch (e) {
      if (e.response?.statusCode == 429) throw DailyLimitReached();
      if (e.response?.statusCode == 503) throw ServiceUnavailable();
      rethrow;
    }
  }

  Future<SourceText> reference(String refKey) async {
    final res = await _dio.get<Map<String, dynamic>>('/v1/references/${Uri.encodeComponent(refKey)}');
    return SourceText.fromJson(res.data!);
  }

  Future<List<ChatSummary>> chats() async {
    final res = await _dio.get<List<dynamic>>('/v1/chats');
    return res.data!.map((c) => ChatSummary.fromJson(c as Map<String, dynamic>)).toList();
  }

  Future<List<ChatMessage>> chatMessages(String chatId) async {
    final res = await _dio.get<Map<String, dynamic>>('/v1/chats/$chatId');
    return (res.data!['messages'] as List)
        .map((m) => ChatMessage.fromHistory(m as Map<String, dynamic>))
        .toList();
  }

  Future<void> report(String messageId, String reason, {String? details}) async {
    await _dio.post('/v1/reports', data: {'message_id': messageId, 'reason': reason, 'details': ?details});
  }

  // ---- account ----

  Future<Profile> me() async {
    final res = await _dio.get<Map<String, dynamic>>('/v1/me');
    return Profile.fromJson(res.data!);
  }

  Future<Profile> updateMe({String? language, String? madhhab, bool clearMadhhab = false}) async {
    final res = await _dio.patch<Map<String, dynamic>>('/v1/me', data: {
      'preferred_language': ?language,
      'madhhab': ?madhhab,
      'clear_madhhab': clearMadhhab,
    });
    return Profile.fromJson(res.data!);
  }

  /// Exchanges a Google / Apple ID token for our token. The current guest token is
  /// sent along so the guest's history is kept.
  Future<void> signIn(String provider, String idToken, {String? name}) async {
    final guest = await _token();
    final res = await _dio.post<Map<String, dynamic>>(
      '/v1/auth/$provider',
      data: {'id_token': idToken, 'name': ?name},
      options: Options(headers: {'Authorization': 'Bearer $guest'}),
    );
    _cachedToken = res.data!['access_token'] as String;
    await _storage.write(key: _tokenKey, value: _cachedToken);
  }

  // ---- fatawa library ----

  Future<List<FatwaSummary>> fatwas({String? query, String? madhhab}) async {
    final res = await _dio.get<List<dynamic>>('/v1/fatwas', queryParameters: {
      if (query != null && query.isNotEmpty) 'q': query,
      'madhhab': ?madhhab,
    });
    return res.data!.map((f) => FatwaSummary.fromJson(f as Map<String, dynamic>)).toList();
  }

  Future<FatwaDetail> fatwa(String id) async {
    final res = await _dio.get<Map<String, dynamic>>('/v1/fatwas/$id');
    return FatwaDetail.fromJson(res.data!);
  }

  // ---- Ask a Scholar ----

  Future<List<ScholarQuestion>> scholarQuestions() async {
    final res = await _dio.get<List<dynamic>>('/v1/scholar-questions');
    return res.data!.map((q) => ScholarQuestion.fromJson(q as Map<String, dynamic>)).toList();
  }

  Future<ScholarQuestion> askScholar(String question, String language) async {
    final res = await _dio.post<Map<String, dynamic>>(
      '/v1/scholar-questions',
      data: {'question': question, 'language': language},
    );
    return ScholarQuestion.fromJson(res.data!);
  }
}

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

final referenceProvider = FutureProvider.family<SourceText, String>(
  (ref, refKey) => ref.watch(apiClientProvider).reference(refKey),
);

final chatListProvider = FutureProvider<List<ChatSummary>>((ref) => ref.watch(apiClientProvider).chats());

final profileProvider = FutureProvider<Profile>((ref) => ref.watch(apiClientProvider).me());

final fatwaProvider = FutureProvider.family<FatwaDetail, String>(
  (ref, id) => ref.watch(apiClientProvider).fatwa(id),
);

final scholarQuestionsProvider = FutureProvider<List<ScholarQuestion>>(
  (ref) => ref.watch(apiClientProvider).scholarQuestions(),
);
