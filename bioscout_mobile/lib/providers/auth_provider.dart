import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../services/api_service.dart';
import '../database/database_helper.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final DatabaseHelper _dbHelper = DatabaseHelper();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  
  bool _isAuthenticated = false;
  String? _token;
  Map<String, dynamic>? _user;
  bool _isLoading = false;
  String? _error;
  bool _isInitialized = false;

  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String? get token => _token;
  Map<String, dynamic>? get user => _user;
  bool get isInitialized => _isInitialized;

  AuthProvider() {
    _initialize();
  }

Future<void> _initialize() async {
  try {
    final storedToken = await _secureStorage.read(key: 'token');
    if (storedToken != null) {
      _token = storedToken;
      _user = await _dbHelper.getUser();
      _isAuthenticated = true;
    }
  } catch (e) {
    debugPrint('Initialization error: $e');
  } finally {
    _isInitialized = true;
    notifyListeners();
  }
}

  Future<void> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.login(username, password);
      _token = response['token'];
      _user = {
        'id': response['user']['id'],
        'username': response['user']['username'],
        'email': response['user']['email'],
      };
      
      // Save to secure storage and local database
      await _secureStorage.write(key: 'token', value: _token);
      await _dbHelper.saveUser(_user!);
      
      _isAuthenticated = true;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _token = null;
      _user = null;
      _isAuthenticated = false;
      
      // Clear secure storage and local database
      await _secureStorage.delete(key: 'token');
      await _dbHelper.deleteUser();
      
      notifyListeners();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  Future<void> checkInitialization() async {
  if (!_isInitialized) {
    await _initialize();
  }
}

  Future<void> register({
    required String username,
    required String email,
    required String password,
    required String password2,
    String? bio,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.register(
        username: username,
        email: email,
        password: password,
        password2: password2,
        bio: bio,
      );
      _token = response['token'];
      _user = {
        'id': response['user']['id'],
        'username': response['user']['username'],
        'email': response['user']['email'],
      };
      
      // Save to secure storage and local database
      await _secureStorage.write(key: 'token', value: _token);
      await _dbHelper.saveUser(_user!);
      
      _isAuthenticated = true;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _token = null;
      _user = null;
      _isAuthenticated = false;
      
      // Clear secure storage and local database
      await _secureStorage.delete(key: 'token');
      await _dbHelper.deleteUser();
      
      notifyListeners();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    _token = null;
    _user = null;
    _isAuthenticated = false;
    
    // Clear secure storage and local database
    await _secureStorage.delete(key: 'token');
    await _dbHelper.deleteUser();
    
    notifyListeners();
  }

  Future<bool> checkAuth() async {
    // No need to re-initialize, just return the state
    return _isAuthenticated;
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
} 