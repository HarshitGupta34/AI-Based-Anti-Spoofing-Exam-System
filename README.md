# AI Based Anti Spoofing Exam System
## Overview

AI Based Anti Spoofing Exam System is a BCA Final Year Major Project developed to ensure fairness and integrity in online examinations using Artificial Intelligence, Computer Vision, and Behavioral Monitoring techniques.

The system continuously verifies the identity of candidates, detects suspicious activities during examinations, records evidence of violations, and provides administrators with detailed reports for review.

Unlike traditional online examination systems, this platform combines face verification, liveness detection, device detection, audio monitoring, and activity tracking to create a secure remote examination environment.


## Key Features

### Student Module
Secure Student Authentication
Exam Rules and Guidelines
Face Registration and Verification
System Compatibility Check
Online Examination Interface
Automatic Result Generation

### AI Monitoring Module
Face Verification
Continuous identity verification during the examination
Detection of unauthorized candidate replacement

### Liveness Detection
Prevents spoofing attempts using photographs or static facial images
Ensures the registered student remains present during the examination

### Multiple Person Detection
Detects the presence of more than one individual in front of the camera

### Electronic Device Detection
Using YOLOv8 Object Detection:

Mobile Phones
Laptops
Remote Controls
Other suspicious electronic devices

### Screen Monitoring
Detects tab switching
Detects window switching
Monitors examination focus

### Keyboard Shortcut Monitoring

Detects prohibited shortcuts such as:

Alt + Tab
Win + Tab
Ctrl + C
Ctrl + V
Ctrl + A
Ctrl + T
Ctrl + W
Print Screen
Ctrl + Alt + Del

### Audio Monitoring
Detects suspicious surrounding sounds
Records audio evidence automatically
### Head Movement Detection
Developed using MediaPipe Face Mesh
Detects:
Looking Left
Looking Right
Looking Up
Looking Down

Note: This module was implemented and tested during development and can be enabled in future releases.

## Evidence Collection System

Whenever suspicious activity is detected:

Video evidence is automatically recorded
Audio evidence is automatically recorded
Timestamp is generated
Violation duration is recorded
Penalty marks are assigned
Trust score is updated automatically

### Admin Dashboard

The administrator can:

Manage Students
Add Students
Update Student Information
Delete Students
View Examination Results
Review Trust Scores
View Violation Reports
Watch Recorded Violation Videos
Listen to Recorded Violation Audio Clips
Analyze When and How Cheating Occurred

This evidence-based review mechanism allows administrators to verify every detected violation.

### Technology Stack
Frontend
HTML5
CSS3
JavaScript
Bootstrap
### Backend
Flask (Python)
### Database
MySQL
### Artificial Intelligence & Computer Vision
OpenCV
YOLOv8
MediaPipe
Face Recognition
### Audio Processing
PyAudio
### Additional Libraries
NumPy
Threading
PyAutoGUI
Keyboard
### System Workflow
Student Login
Rules & Regulations Verification
Face Registration
Face Confirmation
System Compatibility Check
Start Examination
Continuous AI Monitoring
Violation Detection
Evidence Recording
Trust Score Evaluation
Result Generation
Admin Review and Analysis
