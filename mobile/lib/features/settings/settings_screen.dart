import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api_client.dart';
import '../../core/app_language.dart';
import '../../core/config.dart';
import '../../core/models.dart';
import '../../core/settings_controller.dart';
import '../../core/sign_in.dart';
import '../../core/strings.dart';

const _madhhabs = ['hanafi', 'shafii', 'maliki', 'hanbali', 'ahl_e_hadith'];

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = ref.watch(stringsProvider);
    final lang = ref.watch(languageProvider);
    final profile = ref.watch(profileProvider);
    final titleStyle = Theme.of(context).textTheme.titleSmall;

    return Scaffold(
      appBar: AppBar(title: Text(s.settings)),
      body: ListView(
        children: [
          ListTile(title: Text(s.language, style: titleStyle)),
          RadioGroup<AppLanguage>(
            groupValue: lang,
            onChanged: (v) {
              if (v == null) return;
              ref.read(languageProvider.notifier).set(v);
              ref.read(apiClientProvider).updateMe(language: v.code).ignore();
            },
            child: Column(
              children: [
                for (final l in AppLanguage.values) RadioListTile<AppLanguage>(value: l, title: Text(l.label)),
              ],
            ),
          ),
          const Divider(),
          ListTile(title: Text(s.maslak, style: titleStyle), subtitle: Text(s.maslakHelp)),
          profile.when(
            loading: () => const LinearProgressIndicator(),
            error: (_, _) => ListTile(title: Text(s.errorGeneric)),
            data: (p) => _MaslakPicker(current: p.madhhab, s: s),
          ),
          const Divider(),
          ListTile(title: Text(s.account, style: titleStyle)),
          profile.maybeWhen(data: (p) => _AccountSection(profile: p, s: s), orElse: () => const SizedBox()),
          const Divider(),
          ListTile(title: Text(s.about, style: titleStyle)),
          Padding(padding: const EdgeInsets.fromLTRB(16, 0, 16, 8), child: Text(s.aboutBody)),
          ListTile(
            leading: const Icon(Icons.description_outlined),
            title: const Text('Licences'),
            onTap: () => showLicensePage(context: context, applicationName: s.appName),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}

class _MaslakPicker extends ConsumerWidget {
  const _MaslakPicker({required this.current, required this.s});
  final String? current;
  final S s;

  Future<void> _set(WidgetRef ref, String? value) async {
    final api = ref.read(apiClientProvider);
    if (value == null || value.isEmpty) {
      await api.updateMe(clearMadhhab: true);
    } else {
      await api.updateMe(madhhab: value);
    }
    ref.invalidate(profileProvider);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) => RadioGroup<String>(
        groupValue: current ?? '',
        onChanged: (v) => _set(ref, v),
        child: Column(
          children: [
            RadioListTile<String>(value: '', title: Text(s.allSchools)),
            for (final m in _madhhabs) RadioListTile<String>(value: m, title: Text(s.madhhabName(m))),
          ],
        ),
      );
}

class _AccountSection extends ConsumerWidget {
  const _AccountSection({required this.profile, required this.s});
  final Profile profile;
  final S s;

  Future<void> _signIn(BuildContext context, WidgetRef ref, Future<void> Function() action) async {
    final messenger = ScaffoldMessenger.of(context);
    try {
      await action();
      ref.invalidate(profileProvider);
      ref.invalidate(chatListProvider);
    } catch (_) {
      messenger.showSnackBar(SnackBar(content: Text(s.signInFailed)));
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final signIn = ref.read(signInServiceProvider);
    final isApplePlatform = Theme.of(context).platform == TargetPlatform.iOS;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (profile.isGuest) ...[
          Padding(padding: const EdgeInsets.symmetric(horizontal: 16), child: Text(s.guestAccount)),
          const SizedBox(height: 8),
          if (AppConfig.googleSignInConfigured)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: OutlinedButton.icon(
                icon: const Icon(Icons.login),
                label: Text(s.signInGoogle),
                onPressed: () => _signIn(context, ref, signIn.signInWithGoogle),
              ),
            ),
          if (AppConfig.appleSignInConfigured || isApplePlatform)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: OutlinedButton.icon(
                icon: const Icon(Icons.apple),
                label: Text(s.signInApple),
                onPressed: () => _signIn(context, ref, signIn.signInWithApple),
              ),
            ),
        ] else
          ListTile(
            leading: const Icon(Icons.verified_user_outlined),
            title: Text(profile.displayName ?? profile.email ?? s.signedInAs),
            subtitle: Text('${s.signedInAs}: ${profile.signedInWith}'),
          ),
        ListTile(
          leading: Icon(profile.premiumActive ? Icons.workspace_premium : Icons.workspace_premium_outlined),
          title: Text(s.premium),
          subtitle: Text(profile.premiumActive ? s.premiumActive : s.premiumInfo),
        ),
        ListTile(
          leading: const Icon(Icons.badge_outlined),
          title: Text(s.userId),
          subtitle: Text(profile.userId, style: Theme.of(context).textTheme.bodySmall),
          trailing: const Icon(Icons.copy, size: 18),
          onTap: () {
            Clipboard.setData(ClipboardData(text: profile.userId));
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(s.copied)));
          },
        ),
      ],
    );
  }
}
