import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  static Database? _database;

  factory DatabaseHelper() => _instance;

  DatabaseHelper._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    String path = join(await getDatabasesPath(), 'bioscout.db');
    return await openDatabase(
      path,
      version: 1,
      onCreate: _onCreate,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // Users table
    await db.execute('''
      CREATE TABLE users(
        id INTEGER PRIMARY KEY,
        username TEXT,
        email TEXT,
        token TEXT
      )
    ''');

    // Observations table
    await db.execute('''
      CREATE TABLE observations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        species_name TEXT NOT NULL,
        date_observed TEXT NOT NULL,
        location TEXT NOT NULL,
        notes TEXT,
        image_path TEXT,
        is_synced INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    ''');
  }

  // User operations
  Future<void> saveUser(Map<String, dynamic> user) async {
    final db = await database;
    await db.insert('users', user, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<Map<String, dynamic>?> getUser() async {
    final db = await database;
    List<Map<String, dynamic>> users = await db.query('users');
    return users.isNotEmpty ? users.first : null;
  }

  Future<void> deleteUser() async {
    final db = await database;
    await db.delete('users');
  }

  // Observation operations
  Future<int> saveObservation(Map<String, dynamic> observation) async {
    final db = await database;
    return await db.insert('observations', observation);
  }

  Future<List<Map<String, dynamic>>> getUnsyncedObservations() async {
    final db = await database;
    return await db.query(
      'observations',
      where: 'is_synced = ?',
      whereArgs: [0],
      orderBy: 'created_at ASC',
    );
  }

  Future<void> markObservationAsSynced(int id) async {
    final db = await database;
    await db.update(
      'observations',
      {'is_synced': 1},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<List<Map<String, dynamic>>> getAllObservations() async {
    final db = await database;
    return await db.query('observations', orderBy: 'created_at DESC');
  }

  Future<void> updateObservation(Map<String, dynamic> observation) async {
    final db = await database;
    await db.update(
      'observations',
      observation,
      where: 'id = ?',
      whereArgs: [observation['id']],
    );
  }

  Future<void> deleteObservation(int id) async {
    final db = await database;
    await db.delete(
      'observations',
      where: 'id = ?',
      whereArgs: [id],
    );
  }
} 