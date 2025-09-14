# Face Recognition Integration Script for Punjab Government School Attendance System
# This is a sample script showing how to integrate your face recognition system with the attendance database

import requests
import json
from datetime import date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://punjab-attendance.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Sample student IDs in the system
STUDENT_IDS = ['STU001', 'STU002', 'STU003', 'STU004', 'STU005']

def mark_attendance_via_api(student_id, status='present'):
    """
    Mark attendance for a student via the web API
    
    Args:
        student_id (str): Student ID (e.g., 'STU001')
        status (str): 'present' or 'absent'
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        url = f"{API_BASE}/external/mark-attendance"
        params = {
            'student_id': student_id,
            'status': status
        }
        
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully marked {student_id} as {status}")
            print(f"   Response: {result['message']}")
            return True
        else:
            print(f"❌ Failed to mark attendance for {student_id}")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error marking attendance for {student_id}: {str(e)}")
        return False

def get_student_status(student_id):
    """
    Get current attendance status for a student
    
    Args:
        student_id (str): Student ID
        
    Returns:
        dict: Student status data or None if failed
    """
    try:
        url = f"{API_BASE}/student-status/{student_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get status for {student_id}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting status for {student_id}: {str(e)}")
        return None

# Example usage:
if __name__ == "__main__":
    print("🎓 Punjab Government School Attendance - Face Recognition Integration")
    print("=" * 70)
    
    # Example 1: Mark a student as present (this is what your face recognition would do)
    print("\n📸 Simulating face recognition detection...")
    student_detected = "STU001"  # This would come from your face recognition
    
    success = mark_attendance_via_api(student_detected, 'present')
    
    if success:
        print(f"\n📊 Getting updated status for {student_detected}...")
        status = get_student_status(student_detected)
        if status:
            print(f"   Student: {status['name']}")
            print(f"   Overall Attendance: {status['overall_percentage']}%")
            print(f"   Days Present: {status['monthly_stats']['present']}")
            print(f"   Days Absent: {status['monthly_stats']['absent']}")
    
    print("\n" + "=" * 70)
    print("🔗 Integration Points:")
    print(f"   • API Endpoint: {API_BASE}/external/mark-attendance")
    print("   • Method: POST")
    print("   • Parameters: student_id, status")
    print("   • Database: Shared MongoDB instance")
    print("   • Real-time: Changes reflect immediately in web interface")

"""
To integrate with your face recognition system:

1. Install required packages:
   pip install requests python-dotenv

2. In your face recognition code, when you detect a known face:
   
   # Your face recognition logic here
   detected_student_id = recognize_face(camera_frame)
   
   if detected_student_id:
       mark_attendance_via_api(detected_student_id, 'present')

3. The attendance will be automatically updated in the web interface
   and teachers can see real-time attendance data.

4. Database Structure:
   - Students: STU001 (Arjun Singh), STU002 (Priya Kaur), STU003 (Rajesh Kumar), 
             STU004 (Simran Dhillon), STU005 (Harmanpreet Singh)
   - All data stored in MongoDB shared between web app and this script

5. The web interface will show:
   - Manual attendance entry
   - Real-time face recognition updates
   - Student search and status
   - Calendar view of attendance
"""