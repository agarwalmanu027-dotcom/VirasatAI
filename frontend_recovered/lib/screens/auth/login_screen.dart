import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_session.dart';
import '../../app/routes.dart';
import '../../app/theme.dart';
import '../../data/auth_api.dart';
import '../../widgets/auth_background.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, this.startInRegisterMode = false});

  final bool startInRegisterMode;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _nameController = TextEditingController();
  bool _register = false;
  bool _busy = false;
  bool _showPassword = false;

  @override
  void initState() {
    super.initState();
    _register = widget.startInRegisterMode;
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  void _continue() {
    if (!_formKey.currentState!.validate()) return;
    AppSession.instance.signInForDemo(_emailController.text);
    context.go(AppRoutes.home);
  }

  Future<void> _submitAccount() async {
    if (!_formKey.currentState!.validate()) return;
    if (_register && _passwordController.text.length < 8) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Password must be at least 8 characters.')));
      return;
    }
    if (_register && _nameController.text.trim().length < 2) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Enter your name.')));
      return;
    }
    if (!AuthApi.isConfigured) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text(
              'Account server is not connected yet. You can use demo mode.')));
      return;
    }
    setState(() => _busy = true);
    try {
      final result = _register
          ? await AuthApi.register(_nameController.text.trim(),
              _emailController.text.trim(), _passwordController.text)
          : await AuthApi.login(
              _emailController.text.trim(), _passwordController.text);
      if (!mounted) return;
      await AppSession.instance.saveReal(
          email: result.email,
          displayName: result.displayName,
          token: result.token,
          expiresAt: result.expiresAt);
      if (!mounted) return;
      context.go(AppRoutes.home);
    } on AuthApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(error.message)));
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text(
                'Sign-in could not be saved on this phone. Please try again.')));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => AuthBackground(
        child: SafeArea(
          child: LayoutBuilder(
            builder: (context, constraints) => SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 16),
              child: ConstrainedBox(
                constraints:
                    BoxConstraints(minHeight: constraints.maxHeight - 32),
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 440),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Align(
                          alignment: Alignment.centerLeft,
                          child: CircleAvatar(
                            radius: 24,
                            backgroundColor: Color(0xFFF3D6A4),
                            child: Icon(Icons.account_balance_outlined,
                                color: AppTheme.primaryColor),
                          ),
                        ),
                        SizedBox(
                            height: constraints.maxHeight < 620 ? 45 : 110),
                        const Text('VirasatAI',
                            style: TextStyle(
                                color: Colors.white,
                                fontSize: 32,
                                fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        const Text('Stories of India, one place at a time.',
                            style:
                                TextStyle(color: Colors.white70, fontSize: 16)),
                        const SizedBox(height: 28),
                        Container(
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Form(
                            key: _formKey,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                Text(
                                    _register
                                        ? 'Create your account'
                                        : 'Sign in to explore',
                                    style: const TextStyle(
                                        fontSize: 20,
                                        fontWeight: FontWeight.bold,
                                        color: AppTheme.primaryColor)),
                                const SizedBox(height: 8),
                                Text(
                                  AuthApi.isConfigured
                                      ? 'Sign in with the email and password used to create your VirasatAI account. Demo mode does not create a saved account.'
                                      : 'Account server is not connected in this build. Demo mode is available.',
                                  style: const TextStyle(
                                      color: AppTheme.secondaryTextColor),
                                ),
                                const SizedBox(height: 18),
                                if (_register) ...[
                                  TextFormField(
                                    controller: _nameController,
                                    decoration: const InputDecoration(
                                      labelText: 'Your name',
                                      prefixIcon: Icon(Icons.person_outline),
                                      border: OutlineInputBorder(),
                                    ),
                                  ),
                                  const SizedBox(height: 14),
                                ],
                                TextFormField(
                                  controller: _emailController,
                                  keyboardType: TextInputType.emailAddress,
                                  textInputAction: TextInputAction.next,
                                  decoration: const InputDecoration(
                                    labelText: 'Email address',
                                    prefixIcon: Icon(Icons.mail_outline),
                                    border: OutlineInputBorder(),
                                  ),
                                  validator: (value) {
                                    final email = (value ?? '').trim();
                                    if (!RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
                                        .hasMatch(email)) {
                                      return 'Enter a valid email address';
                                    }
                                    return null;
                                  },
                                ),
                                const SizedBox(height: 14),
                                TextFormField(
                                  controller: _passwordController,
                                  obscureText: !_showPassword,
                                  textInputAction: TextInputAction.done,
                                  onFieldSubmitted: (_) => _submitAccount(),
                                  decoration: InputDecoration(
                                    labelText: 'Password',
                                    prefixIcon: const Icon(Icons.lock_outline),
                                    border: const OutlineInputBorder(),
                                    suffixIcon: IconButton(
                                      tooltip: _showPassword
                                          ? 'Hide password'
                                          : 'Show password',
                                      icon: Icon(_showPassword
                                          ? Icons.visibility_off_outlined
                                          : Icons.visibility_outlined),
                                      onPressed: () => setState(
                                          () => _showPassword = !_showPassword),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 18),
                                FilledButton(
                                  onPressed: _busy ? null : _submitAccount,
                                  child: Padding(
                                    padding: const EdgeInsets.symmetric(
                                        vertical: 14),
                                    child: Text(_busy
                                        ? 'Please wait...'
                                        : (_register
                                            ? 'Create account'
                                            : 'Sign in')),
                                  ),
                                ),
                                TextButton(
                                  onPressed: _busy
                                      ? null
                                      : () => setState(
                                          () => _register = !_register),
                                  child: Text(_register
                                      ? 'Already have an account? Sign in'
                                      : 'New here? Create an account'),
                                ),
                                const Divider(height: 24),
                                OutlinedButton(
                                  onPressed: _busy ? null : _continue,
                                  child: const Text('Continue in demo mode'),
                                ),
                                const Padding(
                                  padding: EdgeInsets.only(top: 14),
                                  child: Text(
                                    'After sign-in, your heritage home will open.',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                        color: AppTheme.secondaryTextColor),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      );
}
