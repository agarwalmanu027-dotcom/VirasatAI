import 'package:go_router/go_router.dart';
import 'app_session.dart';
import '../screens/auth/auth_welcome_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/explore/guide_library_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/profile/profile_screen.dart';
import '../screens/placeholder_screen.dart';
import '../screens/result/result_screen.dart';
import '../screens/result/qutub_minar_guide_screen.dart';
import '../screens/result/heritage_guide_screen.dart';
import '../screens/scan/scan_screen.dart';
import '../screens/report/report_issue_screen.dart';

class AppRoutes {
  static const String home = '/home';
  static const String auth = '/auth';
  static const String login = '/login';
  static const String signup = '/signup';
  static const String phone = '/phone';
  static const String scan = '/scan';
  static const String explore = '/explore';
  static const String guideLibrary = '/guides';
  static const String guide = '/guide/:placeId';
  static const String profile = '/profile';
  static const String monumentDetails = '/monument/:id';
  static const String result = '/result/:monumentId';
  static const String damageResult = '/damage-result';
  static const String healthTimeline = '/timeline/:monumentId';
  static const String reportIssue = '/report/:monumentId';

  static final router = GoRouter(
    initialLocation: AppSession.instance.isSignedIn ? home : login,
    refreshListenable: AppSession.instance,
    redirect: (context, state) {
      final path = state.uri.path;
      if (!AppSession.instance.isSignedIn && path != login && path != signup) {
        return login;
      }
      if (AppSession.instance.isSignedIn &&
          (path == login || path == signup || path == '/')) {
        return home;
      }
      return null;
    },
    routes: [
      GoRoute(path: '/', redirect: (context, state) => login),
      GoRoute(
        path: auth,
        builder: (context, state) => const AuthWelcomeScreen(),
      ),
      GoRoute(
        path: home,
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: signup,
        builder: (context, state) =>
            const LoginScreen(startInRegisterMode: true),
      ),
      GoRoute(
        path: phone,
        builder: (context, state) =>
            const PlaceholderScreen(title: 'Phone Authentication'),
      ),
      GoRoute(
        path: scan,
        builder: (context, state) => const ScanScreen(),
      ),
      GoRoute(
        path: explore,
        builder: (context, state) => const GuideLibraryScreen(),
      ),
      GoRoute(
        path: guideLibrary,
        builder: (context, state) => const GuideLibraryScreen(),
      ),
      GoRoute(
        path: guide,
        builder: (context, state) => HeritageGuideScreen(
          placeId: state.pathParameters['placeId'] ?? '',
          initialHindi: state.uri.queryParameters['lang'] == 'hi',
        ),
      ),
      GoRoute(
        path: profile,
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: monumentDetails,
        builder: (context, state) => PlaceholderScreen(
          title: 'Monument Details ${state.pathParameters['id']}',
        ),
      ),
      GoRoute(
        path: result,
        builder: (context, state) {
          final id = state.pathParameters['monumentId'] ?? '';
          final isHindi = state.uri.queryParameters['lang'] == 'hi';
          if (id == 'qutub-minar') {
            return QutubMinarGuideScreen(initialHindi: isHindi);
          }
          if (id == 'taj-mahal') {
            return ResultScreen(monumentId: id, initialHindi: isHindi);
          }
          return const PlaceholderScreen(title: 'Guide coming soon');
        },
      ),
      GoRoute(
        path: damageResult,
        builder: (context, state) =>
            const PlaceholderScreen(title: 'Damage Result'),
      ),
      GoRoute(
        path: healthTimeline,
        builder: (context, state) => PlaceholderScreen(
          title: 'Health Timeline ${state.pathParameters['monumentId'] ?? ''}',
        ),
      ),
      GoRoute(
        path: reportIssue,
        builder: (context, state) => ReportIssueScreen(
          placeId: state.pathParameters['monumentId'] ?? '',
          isHindi: state.uri.queryParameters['lang'] == 'hi',
        ),
      ),
    ],
  );
}
