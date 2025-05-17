import 'package:flutter/material.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'dart:io';
import '../services/api_service.dart';
import '../database/database_helper.dart';
import 'auth_provider.dart';
import 'package:provider/provider.dart';

class ObservationProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final DatabaseHelper _dbHelper = DatabaseHelper();
  List<Map<String, dynamic>> _observations = [];
  bool _isLoading = false;
  bool _isSyncing = false;

  List<Map<String, dynamic>> get observations => _observations;
  bool get isLoading => _isLoading;
  bool get isSyncing => _isSyncing;

  ObservationProvider();

  Future<void> loadObservations({required bool isAuthenticated, required String? token}) async {
    _isLoading = true;
    notifyListeners();

    try {
      // Load from local database first
      _observations = await _dbHelper.getAllObservations();
      notifyListeners();

      // Check connectivity
      final connectivityResult = await Connectivity().checkConnectivity();
      if (connectivityResult != ConnectivityResult.none) {
        // Sync unsynced observations
        await _syncUnsyncedObservations(isAuthenticated: isAuthenticated, token: token);
        if (isAuthenticated && token != null) {
          final apiObservations = await _apiService.getObservations(token);
          _observations = apiObservations.map((obs) => obs as Map<String, dynamic>).toList();
          notifyListeners();
        }
      }
    } catch (e) {
      debugPrint('Error loading observations: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> submitObservation({
    required String speciesName,
    required String dateObserved,
    required String location,
    String? notes,
    File? image,
    required BuildContext context,
  }) async {
    try {
      final observation = {
        'species_name': speciesName,
        'date_observed': dateObserved,
        'location': location,
        'notes': notes,
        'image_path': image?.path,
        'is_synced': 0,
        'created_at': DateTime.now().toIso8601String(),
        'updated_at': DateTime.now().toIso8601String(),
      };

      // Save to local database
      final id = await _dbHelper.saveObservation(observation);
      observation['id'] = id;
      _observations.insert(0, observation);
      notifyListeners();

      // Check connectivity
      final connectivityResult = await Connectivity().checkConnectivity();
      if (connectivityResult != ConnectivityResult.none) {
        // Capture necessary values before await
        final authProvider = Provider.of<AuthProvider>(context, listen: false);
        final bool isAuthenticated = authProvider.isAuthenticated;
        final String? token = authProvider.token;
        if (isAuthenticated && token != null) {
          await _syncObservation(observation, token);
        }
      }
    } catch (e) {
      debugPrint('Error submitting observation: $e');
      rethrow;
    }
  }

  Future<void> _syncUnsyncedObservations({required bool isAuthenticated, required String? token}) async {
    if (_isSyncing) return;
    _isSyncing = true;
    notifyListeners();

    try {
      final unsynced = await _dbHelper.getUnsyncedObservations();
      for (var observation in unsynced) {
        if (isAuthenticated && token != null) {
          await _syncObservation(observation, token);
        }
      }
    } catch (e) {
      debugPrint('Error syncing observations: $e');
    } finally {
      _isSyncing = false;
      notifyListeners();
    }
  }

  Future<void> _syncObservation(Map<String, dynamic> observation, String token) async {
    try {
      final response = await _apiService.submitObservation(
        observation['species_name'],
        observation['date_observed'],
        observation['location'],
        observation['notes'],
        observation['image_path'] != null ? File(observation['image_path']) : null,
        token,
      );

      // Mark as synced
      await _dbHelper.markObservationAsSynced(observation['id']);
      
      // Update local observation with server data
      final index = _observations.indexWhere((obs) => obs['id'] == observation['id']);
      if (index != -1) {
        _observations[index] = response;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error syncing observation: $e');
    }
  }

  Future<void> deleteObservation(int id) async {
    try {
      await _dbHelper.deleteObservation(id);
      _observations.removeWhere((obs) => obs['id'] == id);
      notifyListeners();
    } catch (e) {
      debugPrint('Error deleting observation: $e');
      rethrow;
    }
  }
} 