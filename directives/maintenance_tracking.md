# Maintenance Tracking SOP

This document defines how the vehicle maintenance tracking system operates, specifically integrating with Geotab data.

## 1. Tracking Mechanisms
Vehicles can have maintenance tasks tracked by:
- **Engine Hours**: Cumulative operating time of the engine.
- **Mileage**: Odometer readings.
- **Time**: Calendar intervals (e.g., every 6 months).

## 2. Thresholds and Alerts
- Users define a "Service Interval" (e.g., 5000 miles).
- Users define "Alert Thresholds" (e.g., notify at 500, 250, and 100 miles remaining).
- The system checks these thresholds after every Geotab sync.

## 3. Geotab Synchronization
- The `geotab_sync.py` script runs periodically (via cron or scheduled task).
- It fetches the latest `Odometer` and `EngineHours` for all active vehicles.
- It updates the local database with these values.

## 4. Notifications
- When a threshold is crossed, the `alert_service.py` script generates a notification.
- Notifications are sent via email to the configured admin/group email list.
