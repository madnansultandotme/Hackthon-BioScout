import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'dart:io';

class ApiService {
  late Dio _dio;
  final String baseUrl;

  ApiService() : baseUrl = dotenv.env['API_URL'] ?? 'http://172.31.160.1:8000/api' {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 3),
    ));
  }

  // Auth endpoints
  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await _dio.post('/users/login/', data: {
        'username': username,
        'password': password,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    required String password2,
    String? bio,
  }) async {
    try {
      final response = await _dio.post('/users/register/', data: {
        'username': username,
        'email': email,
        'password': password,
        'password2': password2,
        if (bio != null) 'bio': bio,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> refreshToken(String refreshToken) async {
    try {
      final response = await _dio.post('/users/token/refresh/', data: {
        'refresh': refreshToken,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // User Profile endpoints
  Future<Map<String, dynamic>> getUserProfile(String token) async {
    try {
      final response = await _dio.get(
        '/users/profile/',
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
        ),
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> updateUserProfile(String token, {String? bio}) async {
    try {
      final response = await _dio.patch(
        '/users/profile/',
        data: {
          if (bio != null) 'bio': bio,
        },
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
        ),
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Observation endpoints
  Future<Map<String, dynamic>> submitObservation(
    String speciesName,
    String dateObserved,
    String location,
    String? notes,
    File? image,
    String token,
  ) async {
    try {
      FormData formData = FormData.fromMap({
        'species_name': speciesName,
        'date_observed': dateObserved,
        'location': location,
        if (notes != null) 'notes': notes,
        if (image != null)
          'image': await MultipartFile.fromFile(
            image.path,
            filename: image.path.split('/').last,
          ),
      });

      final response = await _dio.post(
        '/observations/',
        data: formData,
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
        ),
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<dynamic>> getObservations(String token) async {
    try {
      final response = await _dio.get(
        '/observations/',
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
        ),
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getObservationById(String token, int id) async {
    try {
      final response = await _dio.get(
        '/observations/$id/',
        options: Options(
          headers: {'Authorization': 'Bearer $token'},
        ),
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // RAG QA endpoint
  Future<String> askQuestion(String question, String token) async {
    try {
      final response = await _dio.post(
        '/api/rag-qa/',
        data: {'question': question},
        options: Options(
          headers: {'Authorization': 'Token $token'},
        ),
      );
      return response.data['answer'];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Error handling
  String _handleError(DioException error) {
    if (error.response != null) {
      final data = error.response?.data;
      if (data is Map) {
        if (data.containsKey('detail')) {
          return data['detail'];
        } else if (data.containsKey('non_field_errors')) {
          return data['non_field_errors'][0];
        } else {
          // Handle field-specific errors
          final errors = data.values
              .whereType<List>()
              .expand((list) => list)
              .whereType<String>()
              .join(', ');
          return errors.isNotEmpty ? errors : 'An error occurred';
        }
      }
      return 'An error occurred';
    } else if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return 'Connection timeout. Please check your internet connection.';
    } else {
      return 'Network error. Please try again later.';
    }
  }
} 