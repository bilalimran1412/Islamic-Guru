import 'dart:io' show Platform;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:sign_in_with_apple/sign_in_with_apple.dart';

import 'api_client.dart';
import 'config.dart';

/// Native Google / Apple sign-in. The provider's ID token is sent to our
/// backend, which verifies it and links it to the current guest account.
class SignInService {
  SignInService(this._api);
  final ApiClient _api;
  bool _googleReady = false;

  Future<void> signInWithGoogle() async {
    final google = GoogleSignIn.instance;
    if (!_googleReady) {
      await google.initialize(
        clientId: Platform.isIOS && AppConfig.googleIosClientId.isNotEmpty ? AppConfig.googleIosClientId : null,
        serverClientId: AppConfig.googleServerClientId,
      );
      _googleReady = true;
    }
    final account = await google.authenticate();
    final idToken = account.authentication.idToken;
    if (idToken == null) throw StateError('Google returned no ID token');
    await _api.signIn('google', idToken, name: account.displayName);
  }

  Future<void> signInWithApple() async {
    final credential = await SignInWithApple.getAppleIDCredential(
      scopes: [AppleIDAuthorizationScopes.email, AppleIDAuthorizationScopes.fullName],
      // Needed on Android, where Apple sign-in runs in a browser tab.
      webAuthenticationOptions: Platform.isAndroid
          ? WebAuthenticationOptions(
              clientId: AppConfig.appleServiceId,
              redirectUri: Uri.parse(AppConfig.appleRedirectUri),
            )
          : null,
    );
    final token = credential.identityToken;
    if (token == null) throw StateError('Apple returned no identity token');
    final name = [credential.givenName, credential.familyName].whereType<String>().join(' ').trim();
    await _api.signIn('apple', token, name: name.isEmpty ? null : name);
  }
}

final signInServiceProvider = Provider<SignInService>((ref) => SignInService(ref.watch(apiClientProvider)));
