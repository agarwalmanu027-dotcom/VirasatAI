import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_session.dart';
import '../../app/routes.dart';
import '../../app/theme.dart';
import '../../data/auth_api.dart';
import '../../widgets/bottom_nav_bar.dart';
import 'my_activity.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  Future<void> _editName(BuildContext context) async {
    final controller =
        TextEditingController(text: AppSession.instance.displayName);
    final name = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Edit display name'),
        content: TextField(
          controller: controller,
          autofocus: true,
          maxLength: 40,
          decoration: const InputDecoration(labelText: 'Your name'),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, controller.text),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    controller.dispose();
    if (name == null) return;
    final session = AppSession.instance;
    if (session.token == null) {
      session.updateDisplayName(name);
      return;
    }
    try {
      final saved = await AuthApi.updateName(session.token!, name);
      session.updateDisplayName(saved);
    } on AuthApiException catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(error.message)));
      }
    }
  }

  @override
  Widget build(BuildContext context) => PopScope(
        canPop: context.canPop(),
        onPopInvokedWithResult: (didPop, _) {
          if (!didPop) context.go(AppRoutes.home);
        },
        child: AnimatedBuilder(
          animation: AppSession.instance,
          builder: (context, _) {
            final session = AppSession.instance;
            return Scaffold(
              appBar: AppBar(title: const Text('Profile')),
              body: SafeArea(
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 620),
                    child: ListView(
                      padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
                      children: [
                        Container(
                          padding: const EdgeInsets.all(22),
                          decoration: BoxDecoration(
                            color: AppTheme.primaryColor,
                            borderRadius: BorderRadius.circular(22),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const CircleAvatar(
                                radius: 28,
                                backgroundColor: Color(0xFFEED8AB),
                                child: Icon(Icons.person_outline,
                                    color: AppTheme.primaryColor, size: 30),
                              ),
                              const SizedBox(height: 14),
                              Text(
                                session.isSignedIn
                                    ? session.displayName
                                    : 'Guest explorer',
                                style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                session.email ??
                                    'Explore guides without an account',
                                style: const TextStyle(color: Colors.white70),
                              ),
                              const SizedBox(height: 12),
                              Text(
                                session.isDemo
                                    ? 'Demo profile • details last only during this session'
                                    : 'Account profile • name saved on the server',
                                style: const TextStyle(
                                    color: Color(0xFFF2C879), fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 22),
                        const Text('Your journey',
                            style: TextStyle(
                                fontSize: 19, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 10),
                        Card(
                          child: Column(
                            children: [
                              ListTile(
                                leading:
                                    const Icon(Icons.account_balance_outlined),
                                title: const Text('Heritage guides'),
                                subtitle: const Text(
                                    'Explore monuments and nearby places'),
                                trailing: const Icon(Icons.chevron_right),
                                onTap: () =>
                                    context.push(AppRoutes.guideLibrary),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 20),
                        const MyActivity(),
                        const SizedBox(height: 20),
                        const Text('Explore more',
                            style: TextStyle(
                                fontSize: 19, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 10),
                        Card(
                          child: Column(children: [
                            ListTile(
                              leading: const Icon(Icons.info_outline),
                              title: const Text('Languages and offline use'),
                              subtitle: const Text(
                                  'Hindi and English stories are included in the app'),
                              trailing: const Icon(Icons.chevron_right),
                              onTap: () => showAboutDialog(
                                context: context,
                                applicationName: 'VirasatAI',
                                children: [
                                  const Text(
                                      'Hindi and English guide text is packaged with the app. Spoken audio depends on voices available on your device. Other language translation needs an internet connection and is coming later.')
                                ],
                              ),
                            ),
                          ]),
                        ),
                        const SizedBox(height: 20),
                        if (session.isSignedIn) ...[
                          OutlinedButton.icon(
                            onPressed: () => _editName(context),
                            icon: const Icon(Icons.edit_outlined),
                            label: const Text('Edit display name'),
                          ),
                          const SizedBox(height: 8),
                          TextButton.icon(
                            onPressed: () async {
                              final token = session.token;
                              if (token != null) {
                                try {
                                  await AuthApi.logout(token);
                                } catch (_) {
                                  /* Local sign-out still proceeds. */
                                }
                              }
                              session.signOut();
                              if (context.mounted) context.go(AppRoutes.login);
                            },
                            icon: const Icon(Icons.logout),
                            label: Text(session.isDemo
                                ? 'Leave demo session'
                                : 'Sign out'),
                          ),
                        ] else
                          FilledButton.icon(
                            onPressed: () => context.go(AppRoutes.login),
                            icon: const Icon(Icons.person_outline),
                            label: const Text('Preview a profile'),
                          ),
                        const SizedBox(height: 12),
                      ],
                    ),
                  ),
                ),
              ),
              bottomNavigationBar: BottomNavBar(
                currentIndex: 2,
                onTap: (index) {
                  if (index == 3) {
                    context.push(AppRoutes.scan);
                  } else if (index == 0) {
                    context.go(AppRoutes.home);
                  } else if (index == 1) {
                    context.push(AppRoutes.explore);
                  }
                },
              ),
            );
          },
        ),
      );
}
