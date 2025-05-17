import 'package:flutter/material.dart';
import 'dart:io';
import 'package:intl/intl.dart';

class ObservationDetailsScreen extends StatelessWidget {
  const ObservationDetailsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final observation = ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
    final dateFormat = DateFormat('yyyy-MM-dd');
    final date = DateTime.parse(observation['date_observed']);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Observation Details'),
        backgroundColor: Colors.green,
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (observation['image_path'] != null)
              Image.file(
                File(observation['image_path']),
                height: 300,
                width: double.infinity,
                fit: BoxFit.cover,
              ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    observation['species_name'],
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildInfoRow(
                    Icons.calendar_today,
                    'Date Observed',
                    dateFormat.format(date),
                  ),
                  const SizedBox(height: 12),
                  _buildInfoRow(
                    Icons.location_on,
                    'Location',
                    observation['location'],
                  ),
                  if (observation['notes'] != null &&
                      observation['notes'].isNotEmpty) ...[
                    const SizedBox(height: 12),
                    _buildInfoRow(
                      Icons.note,
                      'Notes',
                      observation['notes'],
                    ),
                  ],
                  if (observation['is_synced'] == 0)
                    const Padding(
                      padding: EdgeInsets.only(top: 16),
                      child: Row(
                        children: [
                          Icon(
                            Icons.sync,
                            color: Colors.orange,
                          ),
                          SizedBox(width: 8),
                          Text(
                            'Syncing with server...',
                            style: TextStyle(
                              color: Colors.orange,
                            ),
                          ),
                        ],
                      ),
                    ),
                  if (observation['ai_suggestions'] != null &&
                      observation['ai_suggestions'].isNotEmpty) ...[
                    const SizedBox(height: 24),
                    const Text(
                      'AI Suggestions',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ...observation['ai_suggestions'].map<Widget>((suggestion) {
                      return Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: const Icon(Icons.auto_awesome),
                          title: Text(suggestion['species']),
                          subtitle: Text(
                            'Confidence: ${(suggestion['confidence'] * 100).toStringAsFixed(1)}%',
                          ),
                        ),
                      );
                    }).toList(),
                  ],
                  if (observation['validations'] != null &&
                      observation['validations'].isNotEmpty) ...[
                    const SizedBox(height: 24),
                    const Text(
                      'Validations',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ...observation['validations'].map<Widget>((validation) {
                      return Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: Icon(
                            validation['is_valid']
                                ? Icons.check_circle
                                : Icons.cancel,
                            color: validation['is_valid']
                                ? Colors.green
                                : Colors.red,
                          ),
                          title: Text(validation['validator_name']),
                          subtitle: Text(validation['notes'] ?? ''),
                          trailing: Text(
                            DateFormat('MMM d, y').format(
                              DateTime.parse(validation['date']),
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ],
                  if (observation['correction_requests'] != null &&
                      observation['correction_requests'].isNotEmpty) ...[
                    const SizedBox(height: 24),
                    const Text(
                      'Correction Requests',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ...observation['correction_requests'].map<Widget>((request) {
                      return Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: const Icon(
                            Icons.edit,
                            color: Colors.orange,
                          ),
                          title: Text(request['requester_name']),
                          subtitle: Text(request['suggested_species']),
                          trailing: Text(
                            DateFormat('MMM d, y').format(
                              DateTime.parse(request['date']),
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: Colors.grey),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  color: Colors.grey,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 16,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
} 