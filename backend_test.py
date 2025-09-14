import requests
import sys
from datetime import datetime, date
import json

class PunjabAttendanceAPITester:
    def __init__(self, base_url="https://punjab-attendance.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.student_ids = ["STU001", "STU002", "STU003", "STU004", "STU005"]
        self.expected_students = [
            {"student_id": "STU001", "name": "Arjun Singh"},
            {"student_id": "STU002", "name": "Priya Kaur"},
            {"student_id": "STU003", "name": "Rajesh Kumar"},
            {"student_id": "STU004", "name": "Simran Dhillon"},
            {"student_id": "STU005", "name": "Harmanpreet Singh"}
        ]

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login_valid(self):
        """Test login with valid credentials"""
        success, response = self.run_test(
            "Login with Valid Credentials",
            "POST",
            "login",
            200,
            data={"teacher_id": "abcd@", "password": "1234"}
        )
        if success:
            print(f"   Teacher: {response.get('name', 'Unknown')}")
            return True
        return False

    def test_login_invalid(self):
        """Test login with invalid credentials"""
        success, response = self.run_test(
            "Login with Invalid Credentials",
            "POST",
            "login",
            401,
            data={"teacher_id": "wrong@", "password": "wrong"}
        )
        return success

    def test_get_students(self):
        """Test getting all students"""
        success, response = self.run_test(
            "Get All Students",
            "GET",
            "students",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} students")
            for student in response:
                print(f"   - {student.get('name')} ({student.get('student_id')})")
            
            # Verify expected students are present
            found_students = {s.get('student_id'): s.get('name') for s in response}
            for expected in self.expected_students:
                if expected['student_id'] in found_students:
                    if found_students[expected['student_id']] == expected['name']:
                        print(f"   ✅ {expected['student_id']} - {expected['name']} found correctly")
                    else:
                        print(f"   ⚠️ {expected['student_id']} found but name mismatch: expected {expected['name']}, got {found_students[expected['student_id']]}")
                else:
                    print(f"   ❌ {expected['student_id']} - {expected['name']} not found")
            return True
        return False

    def test_get_attendance_by_date(self):
        """Test getting attendance for a specific date"""
        today = date.today().isoformat()
        success, response = self.run_test(
            f"Get Attendance for Date {today}",
            "GET",
            f"attendance/{today}",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found attendance for {len(response)} students")
            for record in response:
                status = "Present" if record.get('daily_attendance') else "Absent"
                print(f"   - {record.get('name')} ({record.get('student_id')}): {status}")
                print(f"     Monthly: {record.get('monthly_percentage', 0)}%, Overall: {record.get('overall_percentage', 0)}%")
            return True
        return False

    def test_mark_attendance(self):
        """Test marking attendance"""
        today = date.today().isoformat()
        attendance_data = {
            "attendance_records": [
                {"student_id": "STU001", "date": today, "status": "present"},
                {"student_id": "STU002", "date": today, "status": "absent"},
                {"student_id": "STU003", "date": today, "status": "present"}
            ]
        }
        
        success, response = self.run_test(
            "Mark Attendance",
            "POST",
            "attendance",
            200,
            data=attendance_data
        )
        if success:
            print(f"   Message: {response.get('message', 'No message')}")
            return True
        return False

    def test_student_status(self):
        """Test getting student status for each student"""
        all_passed = True
        for student_id in self.student_ids:
            success, response = self.run_test(
                f"Get Student Status - {student_id}",
                "GET",
                f"student-status/{student_id}",
                200
            )
            if success:
                print(f"   Student: {response.get('name')} ({response.get('student_id')})")
                print(f"   Overall Attendance: {response.get('overall_percentage', 0)}%")
                monthly_stats = response.get('monthly_stats', {})
                print(f"   Monthly Stats - Present: {monthly_stats.get('present', 0)}, Absent: {monthly_stats.get('absent', 0)}, Total: {monthly_stats.get('total', 0)}")
                absent_dates = response.get('absent_dates', [])
                print(f"   Absent Days: {len(absent_dates)} days")
            else:
                all_passed = False
        return all_passed

    def test_external_mark_attendance(self):
        """Test the critical external API for face recognition integration"""
        print(f"\n🎯 CRITICAL TEST: External Face Recognition API")
        
        # Test marking attendance via external API
        success, response = self.run_test(
            "External Mark Attendance - STU001 Present",
            "POST",
            "external/mark-attendance?student_id=STU001&status=present",
            200
        )
        if success:
            print(f"   Message: {response.get('message', 'No message')}")
            
            # Verify the attendance was actually marked
            today = date.today().isoformat()
            verify_success, verify_response = self.run_test(
                "Verify External Attendance Marking",
                "GET",
                f"attendance/{today}",
                200
            )
            if verify_success:
                stu001_record = next((r for r in verify_response if r.get('student_id') == 'STU001'), None)
                if stu001_record and stu001_record.get('daily_attendance'):
                    print(f"   ✅ External API successfully marked STU001 as present")
                    return True
                else:
                    print(f"   ❌ External API call succeeded but attendance not reflected")
                    return False
        return False

    def test_student_not_found(self):
        """Test student status for non-existent student"""
        success, response = self.run_test(
            "Get Status for Non-existent Student",
            "GET",
            "student-status/INVALID123",
            404
        )
        return success

def main():
    print("🏫 Punjab Government School Attendance System - API Testing")
    print("=" * 60)
    
    tester = PunjabAttendanceAPITester()
    
    # Test sequence
    tests = [
        ("Login System", [
            tester.test_login_valid,
            tester.test_login_invalid
        ]),
        ("Student Management", [
            tester.test_get_students
        ]),
        ("Attendance System", [
            tester.test_get_attendance_by_date,
            tester.test_mark_attendance
        ]),
        ("Student Status", [
            tester.test_student_status,
            tester.test_student_not_found
        ]),
        ("External Integration (CRITICAL)", [
            tester.test_external_mark_attendance
        ])
    ]
    
    for category, test_functions in tests:
        print(f"\n📋 {category}")
        print("-" * 40)
        for test_func in test_functions:
            test_func()
    
    # Print final results
    print(f"\n📊 FINAL RESULTS")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL TESTS PASSED! Backend is ready for frontend testing.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())