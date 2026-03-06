import json
import os
import sqlite3
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lms.db")
ROLE_OWNER = "owner"
ROLE_MANAGER = "manager"
ROLE_TEACHER = "teacher"
ROLE_PARENT = "parent"
ROLE_STUDENT = "student"
ROLE_LABELS = {
    ROLE_OWNER: "원장",
    ROLE_MANAGER: "매니저",
    ROLE_TEACHER: "강사",
    ROLE_PARENT: "학부모",
    ROLE_STUDENT: "학생",
}
CURRENT_LANG = "ko"
LANG_LABELS = {"ko": "한국어", "en": "English", "zh": "中文"}
NAV_LABELS = {
    "dashboard": "menu.dashboard",
    "users": "menu.users",
    "students": "menu.students",
    "academics": "menu.academics",
    "masterdata": "menu.masterdata",
    "schedule": "menu.schedule",
    "attendance": "menu.attendance",
    "homework": "menu.homework",
    "exams": "menu.exams",
    "counseling": "menu.counseling",
    "payments": "menu.payments",
    "announcements": "menu.announcements",
    "library": "menu.library",
    "logs": "menu.logs",
    "logout": "common.logout",
    "login_as": "common.login_as",
    "lang": "common.language",
}
I18N_TEXTS = {
    "ko": {
        "menu.dashboard": "대시보드", "menu.users": "사용자", "menu.students": "학생관리", "menu.academics": "학사구조", "menu.masterdata": "마스터데이터", "menu.schedule": "스케줄",
        "menu.attendance": "출결", "menu.homework": "숙제", "menu.exams": "시험/성적", "menu.counseling": "상담/특이사항",
        "menu.payments": "수납", "menu.announcements": "공지/알림", "menu.library": "도서대출", "menu.logs": "시스템 로그",
        "common.login_as": "로그인", "common.language": "언어", "common.login": "로그인", "common.logout": "로그아웃",
        "common.save": "저장", "common.edit": "수정", "common.delete": "삭제", "common.search": "검색",
        "common.no_data": "데이터 없음", "common.selected": "선택됨", "common.forbidden": "접근 권한이 없습니다",
        "common.yes": "예", "common.no": "아니오", "common.prev": "이전", "common.next": "다음",
        "login.title": "LMS 로그인", "login.username": "아이디", "login.password": "비밀번호", "login.failed": "로그인 실패",
        "dash.title": "영어학원 LMS 대시보드", "dash.stats": "운영 현황", "dash.quick": "빠른 이동", "dash.users": "사용자", "dash.students": "학생", "dash.classes": "반", "dash.attendance": "출결 기록",
        "users.page_title": "학생/학부모/강사 관리(사용자 기반)", "users.add": "사용자 추가", "users.list": "사용자 목록", "users.saved": "사용자가 저장되었습니다.",
        "students.search": "검색", "students.list": "학생 목록", "common.reset": "초기화",
        "students.detail.title": "학생 상세", "students.detail.back": "학생 목록", "students.detail.edit": "수정",
        "students.detail.section.basic": "기본정보", "students.detail.section.attendance": "최근 출결", "students.detail.section.homework": "최근 숙제 제출/피드백",
        "students.detail.section.exams": "최근 시험/성적", "students.detail.section.counseling": "최근 상담 기록", "students.detail.section.payments": "최근 수납 기록", "students.detail.section.loans": "최근 도서 대출 기록",
        "students.field.student_no": "학생번호", "students.field.name_ko": "한글이름", "students.field.name_en": "영문이름", "students.field.phone": "연락처",
        "students.field.guardian_name": "보호자명", "students.field.guardian_phone": "보호자 연락처", "students.field.class": "현재 반", "students.field.credits": "남은 크레딧",
        "students.field.status": "상태", "students.field.enrolled_at": "입학일", "students.field.leave_period": "휴학 기간", "students.field.memo": "메모",
        "students.field.lesson_date": "날짜", "students.field.note": "메모", "students.field.homework": "숙제", "students.field.submitted": "제출여부", "students.field.submitted_at": "제출일",
        "students.field.feedback": "피드백", "students.field.exam_name": "시험명", "students.field.score": "점수", "students.field.exam_date": "시험일", "students.field.recorded_at": "기록일",
        "students.field.special_note": "특이사항", "students.field.paid_date": "결제일", "students.field.amount": "금액", "students.field.package_hours": "패키지시간",
        "students.field.remaining_classes": "잔여수업수", "students.field.code": "코드", "students.field.title": "제목", "students.field.loaned_at": "대출일", "students.field.returned_at": "반납일",
        "students.msg.saved": "저장되었습니다", "students.msg.pw_saved": "비밀번호가 변경되었습니다", "students.msg.no_user": "연결된 계정이 없습니다", "students.msg.empty_pw": "비밀번호를 입력하세요",
        "status.active": "정상", "status.leave": "휴학", "status.ended": "종료",
        "counseling.title": "상담 기록/학생 특이사항", "counseling.student_id": "학생ID", "counseling.parent_id": "학부모ID", "counseling.memo": "메모", "counseling.special": "특이사항", "counseling.list": "상담 기록",
        "picker.student": "학생 검색 선택", "picker.class": "반 검색 선택", "picker.teacher": "강사 검색 선택",
        "attendance.title": "출결 관리", "attendance.input": "출결 입력", "attendance.list": "출결 기록",
        "homework.title": "숙제 관리", "homework.add": "숙제 등록", "homework.input": "제출/피드백 입력", "homework.list": "숙제 목록", "homework.submissions": "제출/피드백 목록",
        "exams.title": "시험/성적 관리", "exams.add": "시험 등록", "exams.score_input": "점수 입력", "exams.list": "시험 목록", "exams.scores": "점수 목록",
        "payments.title": "수납 기록", "payments.input": "결제 입력", "payments.list": "최근 수납 기록",
        "ann.title": "공지/알림 구조", "ann.write": "공지 작성", "ann.list": "공지 목록", "ann.noti": "알림 데이터",
        "library.title": "도서 대출 관리", "library.book_add": "도서 등록", "library.loan": "대출 처리", "library.return": "반납 처리", "library.books": "도서 목록", "library.history": "대출/반납 이력",
        "field.class_id": "반ID", "field.student_id": "학생ID", "field.teacher_id": "강사ID", "field.date": "날짜", "field.status": "상태", "field.note": "메모", "field.title": "제목", "field.content": "내용", "field.type": "유형", "field.target": "대상", "field.data": "데이터", "field.writer": "작성자", "field.created_at": "생성일", "field.score": "점수",
        "status.present": "출석", "status.late": "지각", "status.absent": "결석", "status.makeup": "보강", "status.cancelled": "휴강",
    },
    "en": {
        "menu.dashboard": "Dashboard", "menu.users": "Users", "menu.students": "Students", "menu.academics": "Academics", "menu.masterdata": "Master Data", "menu.schedule": "Schedule",
        "menu.attendance": "Attendance", "menu.homework": "Homework", "menu.exams": "Exams/Scores", "menu.counseling": "Counseling",
        "menu.payments": "Payments", "menu.announcements": "Announcements", "menu.library": "Library", "menu.logs": "System Logs",
        "common.login_as": "Signed in", "common.language": "Language", "common.login": "Login", "common.logout": "Logout",
        "common.save": "Save", "common.edit": "Edit", "common.delete": "Delete", "common.search": "Search",
        "common.no_data": "No Data", "common.selected": "Selected", "common.forbidden": "Forbidden",
        "common.yes": "Yes", "common.no": "No", "common.prev": "Prev", "common.next": "Next",
        "login.title": "LMS Login", "login.username": "Username", "login.password": "Password", "login.failed": "Login failed",
        "dash.title": "ReadingTown LMS Dashboard", "dash.stats": "Operations Overview", "dash.quick": "Quick Links", "dash.users": "Users", "dash.students": "Students", "dash.classes": "Classes", "dash.attendance": "Attendance Records",
        "users.page_title": "User Management", "users.add": "Add User", "users.list": "User List", "users.saved": "User saved.",
        "students.search": "Search", "students.list": "Student List", "common.reset": "Reset",
        "students.detail.title": "Student Detail", "students.detail.back": "Student List", "students.detail.edit": "Edit",
        "students.detail.section.basic": "Basic Info", "students.detail.section.attendance": "Recent Attendance", "students.detail.section.homework": "Recent Homework Submissions/Feedback",
        "students.detail.section.exams": "Recent Exams/Scores", "students.detail.section.counseling": "Recent Counseling Records", "students.detail.section.payments": "Recent Payments", "students.detail.section.loans": "Recent Book Loans",
        "students.field.student_no": "Student No", "students.field.name_ko": "Korean Name", "students.field.name_en": "English Name", "students.field.phone": "Phone",
        "students.field.guardian_name": "Guardian", "students.field.guardian_phone": "Guardian Phone", "students.field.class": "Class", "students.field.credits": "Remaining Credits",
        "students.field.status": "Status", "students.field.enrolled_at": "Enrollment Date", "students.field.leave_period": "Leave Period", "students.field.memo": "Memo",
        "students.field.lesson_date": "Date", "students.field.note": "Note", "students.field.homework": "Homework", "students.field.submitted": "Submitted", "students.field.submitted_at": "Submitted At",
        "students.field.feedback": "Feedback", "students.field.exam_name": "Exam", "students.field.score": "Score", "students.field.exam_date": "Exam Date", "students.field.recorded_at": "Recorded At",
        "students.field.special_note": "Special Note", "students.field.paid_date": "Paid Date", "students.field.amount": "Amount", "students.field.package_hours": "Package Hours",
        "students.field.remaining_classes": "Remaining Classes", "students.field.code": "Code", "students.field.title": "Title", "students.field.loaned_at": "Loaned At", "students.field.returned_at": "Returned At",
        "students.msg.saved": "Saved successfully", "students.msg.pw_saved": "Password updated", "students.msg.no_user": "No linked user account", "students.msg.empty_pw": "Please enter a password",
        "status.active": "Active", "status.leave": "Leave", "status.ended": "Ended",
        "counseling.title": "Counseling / Student Notes", "counseling.student_id": "Student ID", "counseling.parent_id": "Parent ID", "counseling.memo": "Memo", "counseling.special": "Special Note", "counseling.list": "Counseling Records",
        "picker.student": "Student Picker", "picker.class": "Class Picker", "picker.teacher": "Teacher Picker",
        "attendance.title": "Attendance Management", "attendance.input": "Attendance Entry", "attendance.list": "Attendance Records",
        "homework.title": "Homework Management", "homework.add": "Add Homework", "homework.input": "Submission/Feedback Input", "homework.list": "Homework List", "homework.submissions": "Submission/Feedback List",
        "exams.title": "Exam/Score Management", "exams.add": "Add Exam", "exams.score_input": "Score Input", "exams.list": "Exam List", "exams.scores": "Score List",
        "payments.title": "Payment Records", "payments.input": "Payment Entry", "payments.list": "Recent Payments",
        "ann.title": "Announcements/Notifications", "ann.write": "Write Announcement", "ann.list": "Announcement List", "ann.noti": "Notification Data",
        "library.title": "Library Loan Management", "library.book_add": "Add Book", "library.loan": "Loan Process", "library.return": "Return Process", "library.books": "Book List", "library.history": "Loan/Return History",
        "field.class_id": "Class ID", "field.student_id": "Student ID", "field.teacher_id": "Teacher ID", "field.date": "Date", "field.status": "Status", "field.note": "Note", "field.title": "Title", "field.content": "Content", "field.type": "Type", "field.target": "Target", "field.data": "Data", "field.writer": "Writer", "field.created_at": "Created At", "field.score": "Score",
        "status.present": "Present", "status.late": "Late", "status.absent": "Absent", "status.makeup": "Makeup", "status.cancelled": "Cancelled",
    },
    "zh": {
        "menu.dashboard": "仪表盘", "menu.users": "用户", "menu.students": "学生管理", "menu.academics": "学术结构", "menu.masterdata": "主数据", "menu.schedule": "排课",
        "menu.attendance": "考勤", "menu.homework": "作业", "menu.exams": "考试/成绩", "menu.counseling": "咨询/备注",
        "menu.payments": "收费", "menu.announcements": "公告/通知", "menu.library": "图书借阅", "menu.logs": "系统日志",
        "common.login_as": "当前登录", "common.language": "语言", "common.login": "登录", "common.logout": "退出登录",
        "common.save": "保存", "common.edit": "编辑", "common.delete": "删除", "common.search": "搜索",
        "common.no_data": "无数据", "common.selected": "已选择", "common.forbidden": "无权限",
        "common.yes": "是", "common.no": "否", "common.prev": "上一页", "common.next": "下一页",
        "login.title": "LMS 登录", "login.username": "账号", "login.password": "密码", "login.failed": "登录失败",
        "dash.title": "ReadingTown LMS 仪表盘", "dash.stats": "运营概况", "dash.quick": "快捷入口", "dash.users": "用户", "dash.students": "学生", "dash.classes": "班级", "dash.attendance": "考勤记录",
        "users.page_title": "用户管理", "users.add": "新增用户", "users.list": "用户列表", "users.saved": "用户已保存。",
        "students.search": "搜索", "students.list": "学生列表", "common.reset": "重置",
        "students.detail.title": "学生详情", "students.detail.back": "学生列表", "students.detail.edit": "编辑",
        "students.detail.section.basic": "基本信息", "students.detail.section.attendance": "最近考勤", "students.detail.section.homework": "最近作业提交/反馈",
        "students.detail.section.exams": "最近考试/成绩", "students.detail.section.counseling": "最近咨询记录", "students.detail.section.payments": "最近缴费记录", "students.detail.section.loans": "最近图书借阅记录",
        "students.field.student_no": "学号", "students.field.name_ko": "韩文姓名", "students.field.name_en": "英文姓名", "students.field.phone": "联系电话",
        "students.field.guardian_name": "监护人", "students.field.guardian_phone": "监护人电话", "students.field.class": "当前班级", "students.field.credits": "剩余学分",
        "students.field.status": "状态", "students.field.enrolled_at": "入学日", "students.field.leave_period": "休学期间", "students.field.memo": "备注",
        "students.field.lesson_date": "日期", "students.field.note": "备注", "students.field.homework": "作业", "students.field.submitted": "是否提交", "students.field.submitted_at": "提交日期",
        "students.field.feedback": "反馈", "students.field.exam_name": "考试名", "students.field.score": "分数", "students.field.exam_date": "考试日期", "students.field.recorded_at": "记录日",
        "students.field.special_note": "特殊事项", "students.field.paid_date": "支付日", "students.field.amount": "金额", "students.field.package_hours": "套餐课时",
        "students.field.remaining_classes": "剩余课次", "students.field.code": "编码", "students.field.title": "标题", "students.field.loaned_at": "借出日", "students.field.returned_at": "归还日",
        "students.msg.saved": "已保存", "students.msg.pw_saved": "密码已更新", "students.msg.no_user": "未关联用户账号", "students.msg.empty_pw": "请输入密码",
        "status.active": "正常", "status.leave": "休学", "status.ended": "结束",
        "counseling.title": "咨询记录/学生备注", "counseling.student_id": "学生ID", "counseling.parent_id": "家长ID", "counseling.memo": "备注", "counseling.special": "特殊事项", "counseling.list": "咨询记录",
        "picker.student": "学生搜索选择", "picker.class": "班级搜索选择", "picker.teacher": "教师搜索选择",
        "attendance.title": "考勤管理", "attendance.input": "考勤录入", "attendance.list": "考勤记录",
        "homework.title": "作业管理", "homework.add": "作业登记", "homework.input": "提交/反馈录入", "homework.list": "作业列表", "homework.submissions": "提交/反馈列表",
        "exams.title": "考试/成绩管理", "exams.add": "考试登记", "exams.score_input": "成绩录入", "exams.list": "考试列表", "exams.scores": "成绩列表",
        "payments.title": "缴费记录", "payments.input": "缴费录入", "payments.list": "最近缴费记录",
        "ann.title": "公告/通知结构", "ann.write": "发布公告", "ann.list": "公告列表", "ann.noti": "通知数据",
        "library.title": "图书借阅管理", "library.book_add": "登记图书", "library.loan": "借出处理", "library.return": "归还处理", "library.books": "图书列表", "library.history": "借还记录",
        "field.class_id": "班级ID", "field.student_id": "学生ID", "field.teacher_id": "教师ID", "field.date": "日期", "field.status": "状态", "field.note": "备注", "field.title": "标题", "field.content": "内容", "field.type": "类型", "field.target": "对象", "field.data": "数据", "field.writer": "创建者", "field.created_at": "创建时间", "field.score": "分数",
        "status.present": "出勤", "status.late": "迟到", "status.absent": "缺勤", "status.makeup": "补课", "status.cancelled": "停课",
    },
}

I18N_TEXTS["ko"].update({
    "common.add": "추가", "role.owner": "원장", "role.manager": "매니저", "role.teacher": "강사", "role.parent": "학부모", "role.student": "학생",
    "login.default_accounts": "기본 계정: owner/1234, manager/1234, teacher/1234, parent/1234, student/1234",
    "field.id": "ID", "field.name": "이름", "field.role": "역할", "field.student": "학생", "field.submitted": "제출", "field.homework_title": "숙제명", "field.due_date": "마감일",
    "field.submission_count": "제출수", "field.total_targets": "총대상(등록수)", "field.avg_score": "평균점수", "field.score_entries": "입력건수",
    "students.field.leave_start_date": "휴학시작", "students.field.leave_end_date": "휴학종료", "students.password_reset": "학생 계정 비밀번호 변경", "students.new_password": "새 비밀번호",
    "academics.title": "코스/레벨/반/시간표 관리", "academics.register": "등록", "academics.course": "코스", "academics.level": "레벨", "academics.course_name": "코스명", "academics.level_name": "레벨명",
    "academics.class_name": "반명", "academics.class_list": "반 목록", "academics.course_id": "코스ID", "academics.level_id": "레벨ID", "academics.schedule_class_id": "시간표 반ID",
    "academics.day_of_week": "요일", "academics.start_time": "시작", "academics.end_time": "종료", "academics.teacher": "담당 강사", "academics.student_count": "학생 수", "academics.schedule": "시간표",
    "academics.class_detail.title": "반 상세", "academics.back_to_list": "학사구조 목록", "academics.basic_info": "기본정보", "academics.course_level": "코스/레벨", "academics.students": "소속 학생",
    "academics.sort": "정렬", "academics.sort_name": "이름 정렬", "academics.sort_student_no": "학생번호 정렬", "academics.sort_status": "상태 정렬", "academics.export_students_csv": "학생 CSV 내보내기", "academics.export_attendance_csv": "출결 CSV 내보내기",
    "academics.recent_attendance": "최근 출결", "academics.recent_homework": "최근 숙제", "academics.recent_exams": "최근 시험/성적",
    "forbidden.teacher_class_only": "담당 반만 처리할 수 있습니다", "forbidden.teacher_exam_only": "담당 시험만 처리할 수 있습니다",
    "library.not_found": "도서를 찾을 수 없습니다", "library.loan_done": "대여 완료", "server.start": "LMS 서버 실행",
    "academics.timetable_title": "시간표 관리", "academics.timetable_desc": "주간 수업 배치와 수업별 업무 이동을 관리합니다.", "academics.filter": "필터", "academics.week_prev": "이전 주", "academics.week_current": "현재 주", "academics.week_next": "다음 주",
    "academics.day_filter": "요일", "academics.teacher_filter": "강사", "academics.classroom_filter": "교실", "academics.course_level_filter": "코스/레벨", "academics.class_filter": "반 검색", "academics.search": "검색", "academics.add_lesson": "새 수업 추가",
    "academics.timetable": "주간 타임테이블", "academics.time_slot": "시간대", "academics.teacher_room": "강사/교실", "academics.students_summary": "학생", "academics.more_students": "+더보기", "academics.view_class": "반 상세", "academics.go_attendance": "출결", "academics.go_homework": "숙제", "academics.go_exams": "성적",
    "academics.lesson_detail": "수업 상세", "academics.edit_schedule": "수업 수정", "academics.schedule_form": "시간표 등록/수정", "academics.schedule_pick_class": "반 선택", "academics.schedule_pick_teacher": "강사 선택", "academics.schedule_teacher_auto": "반 담당 강사가 기본 선택됩니다", "academics.schedule_autofill": "선택한 반 정보를 자동으로 불러옵니다", "academics.schedule_pick_day": "요일 선택", "academics.schedule_pick_time": "시간 선택", "academics.schedule_pick_room": "교실 선택", "academics.schedule_pick_status": "상태 선택", "academics.schedule_pick_student": "학생", "academics.go_structure": "학사구조 관리로 이동", "academics.validation_class_required": "반을 먼저 선택하세요", "academics.validation_end_before_start": "종료 시간이 시작 시간보다 이를 수 없습니다", "academics.validation_conflict_class": "같은 반의 시간표가 겹칩니다", "academics.validation_conflict_teacher": "같은 강사의 시간표가 겹칩니다", "academics.validation_conflict_room": "같은 교실의 시간표가 겹칩니다", "academics.saved": "시간표가 저장되었습니다", "academics.updated": "시간표가 수정되었습니다", "academics.day_all": "전체", "academics.status": "상태", "academics.classroom": "교실"
})
I18N_TEXTS["en"].update({
    "common.add": "Add", "role.owner": "Owner", "role.manager": "Manager", "role.teacher": "Teacher", "role.parent": "Parent", "role.student": "Student",
    "login.default_accounts": "Default accounts: owner/1234, manager/1234, teacher/1234, parent/1234, student/1234",
    "field.id": "ID", "field.name": "Name", "field.role": "Role", "field.student": "Student", "field.submitted": "Submitted", "field.homework_title": "Homework", "field.due_date": "Due Date",
    "field.submission_count": "Submissions", "field.total_targets": "Total Targets", "field.avg_score": "Average Score", "field.score_entries": "Score Entries",
    "students.field.leave_start_date": "Leave Start", "students.field.leave_end_date": "Leave End", "students.password_reset": "Reset Student Password", "students.new_password": "New Password",
    "academics.title": "Course/Level/Class/Schedule", "academics.register": "Register", "academics.course": "Course", "academics.level": "Level", "academics.course_name": "Course Name", "academics.level_name": "Level Name",
    "academics.class_name": "Class Name", "academics.class_list": "Class List", "academics.course_id": "Course ID", "academics.level_id": "Level ID", "academics.schedule_class_id": "Schedule Class ID",
    "academics.day_of_week": "Day", "academics.start_time": "Start", "academics.end_time": "End", "academics.teacher": "Teacher", "academics.student_count": "Students", "academics.schedule": "Schedule",
    "academics.class_detail.title": "Class Detail", "academics.back_to_list": "Academics List", "academics.basic_info": "Basic Info", "academics.course_level": "Course/Level", "academics.students": "Class Students",
    "academics.sort": "Sort", "academics.sort_name": "Sort by Name", "academics.sort_student_no": "Sort by Student No", "academics.sort_status": "Sort by Status", "academics.export_students_csv": "Export Students CSV", "academics.export_attendance_csv": "Export Attendance CSV",
    "academics.recent_attendance": "Recent Attendance", "academics.recent_homework": "Recent Homework", "academics.recent_exams": "Recent Exams/Scores",
    "forbidden.teacher_class_only": "Teacher can only access assigned classes", "forbidden.teacher_exam_only": "Teacher can only access assigned exams",
    "library.not_found": "Book not found", "library.loan_done": "Loan completed", "server.start": "LMS server running",
    "academics.timetable_title": "Timetable Management", "academics.timetable_desc": "Manage weekly lesson placement and quick jumps to class operations.", "academics.filter": "Filters", "academics.week_prev": "Previous Week", "academics.week_current": "Current Week", "academics.week_next": "Next Week",
    "academics.day_filter": "Day", "academics.teacher_filter": "Teacher", "academics.classroom_filter": "Classroom", "academics.course_level_filter": "Course/Level", "academics.class_filter": "Class Search", "academics.search": "Search", "academics.add_lesson": "Add Lesson",
    "academics.timetable": "Weekly Timetable", "academics.time_slot": "Time Slots", "academics.teacher_room": "Teacher/Room", "academics.students_summary": "Students", "academics.more_students": "+more", "academics.view_class": "Class Detail", "academics.go_attendance": "Attendance", "academics.go_homework": "Homework", "academics.go_exams": "Scores",
    "academics.lesson_detail": "Lesson Detail", "academics.edit_schedule": "Edit Lesson", "academics.schedule_form": "Schedule Create/Edit", "academics.schedule_pick_class": "Select Class", "academics.schedule_pick_teacher": "Select Teacher", "academics.schedule_teacher_auto": "Class teacher is selected by default", "academics.schedule_autofill": "Class info is auto-filled from selected class", "academics.schedule_pick_day": "Select Day", "academics.schedule_pick_time": "Select Time", "academics.schedule_pick_room": "Select Classroom", "academics.schedule_pick_status": "Select Status", "academics.schedule_pick_student": "Students", "academics.go_structure": "Go to academic structure management", "academics.validation_class_required": "Please select a class first", "academics.validation_end_before_start": "End time must be after start time", "academics.validation_conflict_class": "Class schedule conflicts with existing slot", "academics.validation_conflict_teacher": "Teacher schedule conflicts with existing slot", "academics.validation_conflict_room": "Classroom schedule conflicts with existing slot", "academics.saved": "Schedule saved", "academics.updated": "Schedule updated", "academics.day_all": "All", "academics.status": "Status", "academics.classroom": "Classroom"
})
I18N_TEXTS["zh"].update({
    "common.add": "添加", "role.owner": "院长", "role.manager": "经理", "role.teacher": "教师", "role.parent": "家长", "role.student": "学生",
    "login.default_accounts": "默认账号: owner/1234, manager/1234, teacher/1234, parent/1234, student/1234",
    "field.id": "ID", "field.name": "姓名", "field.role": "角色", "field.student": "学生", "field.submitted": "提交", "field.homework_title": "作业名", "field.due_date": "截止日",
    "field.submission_count": "提交数", "field.total_targets": "总对象", "field.avg_score": "平均分", "field.score_entries": "录入数",
    "students.field.leave_start_date": "休学开始", "students.field.leave_end_date": "休学结束", "students.password_reset": "重置学生密码", "students.new_password": "新密码",
    "academics.title": "课程/级别/班级/课表管理", "academics.register": "登记", "academics.course": "课程", "academics.level": "级别", "academics.course_name": "课程名", "academics.level_name": "级别名",
    "academics.class_name": "班级名", "academics.class_list": "班级列表", "academics.course_id": "课程ID", "academics.level_id": "级别ID", "academics.schedule_class_id": "课表班级ID",
    "academics.day_of_week": "星期", "academics.start_time": "开始", "academics.end_time": "结束", "academics.teacher": "负责教师", "academics.student_count": "学生数", "academics.schedule": "课表",
    "academics.class_detail.title": "班级详情", "academics.back_to_list": "学术结构列表", "academics.basic_info": "基本信息", "academics.course_level": "课程/级别", "academics.students": "所属学生",
    "academics.sort": "排序", "academics.sort_name": "按姓名排序", "academics.sort_student_no": "按学号排序", "academics.sort_status": "按状态排序", "academics.export_students_csv": "导出学生CSV", "academics.export_attendance_csv": "导出考勤CSV",
    "academics.recent_attendance": "最近考勤", "academics.recent_homework": "最近作业", "academics.recent_exams": "最近考试/成绩",
    "forbidden.teacher_class_only": "仅可处理负责班级", "forbidden.teacher_exam_only": "仅可处理负责考试",
    "library.not_found": "未找到图书", "library.loan_done": "借阅完成", "server.start": "LMS 服务已启动",
    "academics.timetable_title": "课表管理", "academics.timetable_desc": "管理每周课程排布并快速跳转到班级业务。", "academics.filter": "筛选", "academics.week_prev": "上一周", "academics.week_current": "本周", "academics.week_next": "下一周",
    "academics.day_filter": "星期", "academics.teacher_filter": "教师", "academics.classroom_filter": "教室", "academics.course_level_filter": "课程/级别", "academics.class_filter": "班级搜索", "academics.search": "搜索", "academics.add_lesson": "新增课程",
    "academics.timetable": "周课表", "academics.time_slot": "时间段", "academics.teacher_room": "教师/教室", "academics.students_summary": "学生", "academics.more_students": "+更多", "academics.view_class": "班级详情", "academics.go_attendance": "考勤", "academics.go_homework": "作业", "academics.go_exams": "成绩",
    "academics.lesson_detail": "课程详情", "academics.edit_schedule": "编辑课程", "academics.schedule_form": "课表新增/编辑", "academics.schedule_pick_class": "选择班级", "academics.schedule_pick_teacher": "选择教师", "academics.schedule_teacher_auto": "默认选择班级负责教师", "academics.schedule_autofill": "所选班级信息将自动填充", "academics.schedule_pick_day": "选择星期", "academics.schedule_pick_time": "选择时间", "academics.schedule_pick_room": "选择教室", "academics.schedule_pick_status": "选择状态", "academics.schedule_pick_student": "学生", "academics.go_structure": "前往学术结构管理", "academics.validation_class_required": "请先选择班级", "academics.validation_end_before_start": "结束时间必须晚于开始时间", "academics.validation_conflict_class": "同一班级时间冲突", "academics.validation_conflict_teacher": "同一教师时间冲突", "academics.validation_conflict_room": "同一教室时间冲突", "academics.saved": "课表已保存", "academics.updated": "课表已更新", "academics.day_all": "全部", "academics.status": "状态", "academics.classroom": "教室"
})

def load_locale_files():
    locales_dir = os.path.join(BASE_DIR, "locales")
    if not os.path.isdir(locales_dir):
        return
    for fp in sorted(Path(locales_dir).glob("*.json")):
        code = fp.stem.lower()
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        labels = data.pop("__labels__", {}) if isinstance(data.get("__labels__", {}), dict) else {}
        base = I18N_TEXTS.get(code, {}).copy()
        base.update(data)
        I18N_TEXTS[code] = base
        if isinstance(labels.get("lang"), str) and labels["lang"].strip():
            LANG_LABELS[code] = labels["lang"].strip()
        elif code not in LANG_LABELS:
            LANG_LABELS[code] = code


load_locale_files()
SUPPORTED_LANGS = set(I18N_TEXTS.keys())

NAV_PATHS = {
    "dashboard": "/dashboard",
    "users": "/users",
    "students": "/students",
    "academics": "/academics",
    "masterdata": "/masterdata",
    "schedule": "/schedule",
    "attendance": "/attendance",
    "homework": "/homework",
    "exams": "/exams",
    "counseling": "/counseling",
    "payments": "/payments",
    "announcements": "/announcements",
    "library": "/library",
    "logs": "/logs",
}
ROLE_MENU_KEYS = {
    ROLE_OWNER: ["dashboard", "users", "students", "masterdata", "schedule", "attendance", "homework", "exams", "counseling", "payments", "announcements", "library", "logs"],
    ROLE_MANAGER: ["dashboard", "students", "masterdata", "schedule", "attendance", "homework", "exams", "counseling", "payments", "announcements", "library"],
    ROLE_TEACHER: ["dashboard", "students", "schedule", "attendance", "homework", "exams", "counseling", "announcements", "library"],
    ROLE_PARENT: ["dashboard", "students", "attendance", "homework", "exams", "payments", "announcements"],
    ROLE_STUDENT: ["dashboard", "students", "attendance", "homework", "exams", "announcements"],
}
def t(key, lang=None):
    lang = lang or CURRENT_LANG
    table = I18N_TEXTS.get(lang, I18N_TEXTS["ko"])
    return table.get(key, I18N_TEXTS["ko"].get(key, key))
def menu_t(key, lang=None):
    token = NAV_LABELS.get(key, key)
    return t(token, lang)
def status_t(status, lang=None):
    return t(f"status.{status}", lang)

def attendance_status_t(status, lang=None):
    return t(f"status.{status}", lang)

def role_label(role, lang=None):
    return t(f"role.{role}", lang)

def safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default

def day_sort_value(day_text):
    days = {"mon":1,"monday":1,"tue":2,"tues":2,"tuesday":2,"wed":3,"wednesday":3,"thu":4,"thursday":4,"fri":5,"friday":5,"sat":6,"saturday":6,"sun":7,"sunday":7,
            "월":1,"화":2,"수":3,"목":4,"금":5,"토":6,"일":7,"周一":1,"周二":2,"周三":3,"周四":4,"周五":5,"周六":6,"周日":7,"星期一":1,"星期二":2,"星期三":3,"星期四":4,"星期五":5,"星期六":6,"星期日":7}
    k = (day_text or "").strip().lower()
    return days.get(k, 99)

def parse_hhmm(v):
    if not v or ":" not in v:
        return None
    try:
        h, m = v.split(":", 1)
        return int(h) * 60 + int(m)
    except Exception:
        return None


def is_valid_date(v):
    if not v:
        return False
    try:
        datetime.strptime(v, "%Y-%m-%d")
        return True
    except Exception:
        return False


def as_int(v):
    try:
        return int(str(v).strip())
    except Exception:
        return None


def as_float(v):
    try:
        return float(str(v).strip())
    except Exception:
        return None


def add_error(errors, field, msg):
    errors.append(f"- {field}: {msg}")


def format_errors(errors):
    if not errors:
        return ""
    return "<br>".join(errors)


def ensure_exists(conn, table, value, field="id", extra_where="", extra_params=()):
    if value is None or str(value).strip() == "":
        return False
    sql = f"SELECT 1 FROM {table} WHERE {field}=?"
    params = [value]
    if extra_where:
        sql += f" AND {extra_where}"
        params.extend(extra_params)
    return conn.execute(sql, tuple(params)).fetchone() is not None


def ensure_logs_table(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS app_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      level TEXT NOT NULL,
      route TEXT,
      user_id INTEGER,
      message TEXT NOT NULL,
      detail TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY(user_id) REFERENCES users(id)
    )""")


def log_event(conn, level, route, message, detail="", user_id=None):
    try:
        conn.execute(
            "INSERT INTO app_logs(level, route, user_id, message, detail, created_at) VALUES(?,?,?,?,?,?)",
            (level, route, user_id, message, detail[:4000] if detail else None, now()),
        )
        conn.commit()
    except Exception:
        pass

def is_time_overlap(a_start, a_end, b_start, b_end):
    a1, a2, b1, b2 = parse_hhmm(a_start), parse_hhmm(a_end), parse_hhmm(b_start), parse_hhmm(b_end)
    if None in (a1, a2, b1, b2):
        return False
    return not (a2 <= b1 or b2 <= a1)

def ensure_schedule_columns(conn):
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(schedules)").fetchall()}
    if "classroom" not in cols:
        conn.execute("ALTER TABLE schedules ADD COLUMN classroom TEXT")
    if "status" not in cols:
        conn.execute("ALTER TABLE schedules ADD COLUMN status TEXT DEFAULT 'active'")
    if "note" not in cols:
        conn.execute("ALTER TABLE schedules ADD COLUMN note TEXT")
    if "teacher_id" not in cols:
        conn.execute("ALTER TABLE schedules ADD COLUMN teacher_id INTEGER")


def ensure_extended_columns(conn):
    ucols = {r["name"] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
    if "teacher_type" not in ucols:
        conn.execute("ALTER TABLE users ADD COLUMN teacher_type TEXT")

    ccols = {r["name"] for r in conn.execute("PRAGMA table_info(classes)").fetchall()}
    if "foreign_teacher_id" not in ccols:
        conn.execute("ALTER TABLE classes ADD COLUMN foreign_teacher_id INTEGER")
    if "chinese_teacher_id" not in ccols:
        conn.execute("ALTER TABLE classes ADD COLUMN chinese_teacher_id INTEGER")

    scols = {r["name"] for r in conn.execute("PRAGMA table_info(schedules)").fetchall()}
    if "room_id" not in scols:
        conn.execute("ALTER TABLE schedules ADD COLUMN room_id INTEGER")
    if "foreign_teacher_id" not in scols:
        conn.execute("ALTER TABLE schedules ADD COLUMN foreign_teacher_id INTEGER")
    if "chinese_teacher_id" not in scols:
        conn.execute("ALTER TABLE schedules ADD COLUMN chinese_teacher_id INTEGER")
    if "substitute_foreign_teacher_id" not in scols:
        conn.execute("ALTER TABLE schedules ADD COLUMN substitute_foreign_teacher_id INTEGER")
    if "substitute_chinese_teacher_id" not in scols:
        conn.execute("ALTER TABLE schedules ADD COLUMN substitute_chinese_teacher_id INTEGER")
    if "substitute_reason" not in scols:
        conn.execute("ALTER TABLE schedules ADD COLUMN substitute_reason TEXT")

    rcols = {r["name"] for r in conn.execute("PRAGMA table_info(classrooms)").fetchall()}
    if "room_code" not in rcols:
        conn.execute("ALTER TABLE classrooms ADD COLUMN room_code TEXT")
    if "room_name" not in rcols:
        conn.execute("ALTER TABLE classrooms ADD COLUMN room_name TEXT")
    if "status" not in rcols:
        conn.execute("ALTER TABLE classrooms ADD COLUMN status TEXT DEFAULT 'active'")
    if "memo" not in rcols:
        conn.execute("ALTER TABLE classrooms ADD COLUMN memo TEXT")
def ensure_master_tables(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS classrooms (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      created_at TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS time_slots (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      label TEXT NOT NULL UNIQUE,
      start_time TEXT NOT NULL,
      end_time TEXT NOT NULL,
      created_at TEXT NOT NULL
    )""")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def hash_pw(pw: str) -> str:
    # 단순 데모용
    import hashlib
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()
def now():
    return datetime.utcnow().isoformat()
def init_db():
    conn = get_db()
    with open(os.path.join(BASE_DIR, "schema.sql"), "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    ensure_schedule_columns(conn)
    ensure_extended_columns(conn)
    ensure_master_tables(conn)
    ensure_logs_table(conn)
    cur = conn.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()["c"] == 0:
        users = [
            ("원장", "owner", "owner", "1234"),
            ("매니저", "manager", "manager", "1234"),
            ("강사", "teacher", "teacher", "1234"),
            ("학부모", "parent", "parent", "1234"),
            ("학생", "student", "student", "1234"),
        ]
        for name, username, role, pw in users:
            conn.execute(
                "INSERT INTO users(name, username, password_hash, role, created_at) VALUES(?,?,?,?,?)",
                (name, username, hash_pw(pw), role, now()),
            )
    # 기존 student 역할 사용자에 대한 학생 프로필 보강
    student_users = conn.execute("SELECT id, name FROM users WHERE role=?", (ROLE_STUDENT,)).fetchall()
    for su in student_users:
        exists = conn.execute("SELECT id FROM students WHERE user_id=?", (su["id"],)).fetchone()
        if not exists:
            conn.execute(
                """INSERT INTO students(
                user_id, student_no, name_ko, status, created_at
                ) VALUES(?,?,?,?,?)""",
                (su["id"], f"S{su['id']:04d}", su["name"], "active", now()),
            )
    conn.commit()
    conn.close()
def parse_query(environ):
    return {k: v[0] for k, v in parse_qs(environ.get("QUERY_STRING", "")).items()}
def get_lang(environ):
    q = parse_query(environ)
    lang = q.get("lang", "").strip().lower()
    if lang in SUPPORTED_LANGS:
        return lang
    cookies = parse_cookie(environ.get("HTTP_COOKIE", ""))
    cookie_lang = (cookies.get("lang") or "").strip().lower()
    if cookie_lang in SUPPORTED_LANGS:
        return cookie_lang
    return "ko"
def parse_body(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length) if length > 0 else b""
    ctype = environ.get("CONTENT_TYPE", "")
    if "application/json" in ctype:
        return json.loads(body.decode("utf-8") or "{}")
    return {k: v[0] for k, v in parse_qs(body.decode("utf-8")).items()}
def parse_cookie(cookie):
    out = {}
    if not cookie:
        return out
    for part in cookie.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            out[k] = v
    return out
def current_user(environ):
    cookies = parse_cookie(environ.get("HTTP_COOKIE", ""))
    token = cookies.get("session")
    if not token:
        return None
    conn = get_db()
    row = conn.execute(
        "SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?", (token,)
    ).fetchone()
    conn.close()
    return row
def render_html(title, body, user=None, lang=None, current_menu=None, flash_msg="", flash_type="success"):
    lang = lang or CURRENT_LANG
    css = """
    <style>
      * { box-sizing: border-box; }
      body { margin:0; font-family:Arial, sans-serif; background:#f5f7fb; color:#1f2937; }
      .app { display:flex; min-height:100vh; }
      .sidebar { width:240px; background:#111827; color:#e5e7eb; padding:18px 14px; }
      .brand { font-size:18px; font-weight:700; margin-bottom:18px; }
      .nav-link { display:block; color:#cbd5e1; text-decoration:none; padding:8px 10px; border-radius:8px; margin-bottom:6px; }
      .nav-link:hover { background:#1f2937; color:white; }
      .nav-link.active { background:#2563eb; color:white; }
      .main { flex:1; padding:18px 22px; }
      .topbar { background:white; border:1px solid #e5e7eb; border-radius:12px; padding:10px 14px; display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; }
      .page-title { margin:0 0 14px 0; font-size:24px; }
      .card { background:white; border:1px solid #e5e7eb; border-radius:12px; padding:14px; margin-bottom:14px; }
      .card h3, .card h4 { margin:0 0 10px 0; }
      .filter-row { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
      input, select, textarea { border:1px solid #d1d5db; border-radius:8px; padding:7px 9px; }
      button, .btn { background:#2563eb; color:white; border:none; border-radius:8px; padding:8px 12px; text-decoration:none; display:inline-block; }
      .btn.secondary { background:#6b7280; }
      table { width:100%; border-collapse:collapse; background:white; }
      th, td { border:1px solid #e5e7eb; padding:8px; text-align:left; vertical-align:top; }
      th { background:#f9fafb; }
      .badge { display:inline-block; padding:3px 8px; border-radius:999px; font-size:12px; background:#e5e7eb; }
      .badge.active { background:#dcfce7; color:#166534; }
      .badge.leave { background:#fef3c7; color:#92400e; }
      .badge.ended { background:#fee2e2; color:#991b1b; }
      .empty-msg { color:#6b7280; font-style:italic; }
      .flash { border-radius:10px; padding:10px 12px; margin-bottom:12px; }
      .flash.success { background:#ecfdf5; color:#065f46; border:1px solid #a7f3d0; }
      .flash.error { background:#fef2f2; color:#991b1b; border:1px solid #fecaca; }
      .timetable-wrap { overflow:auto; border:1px solid #e5e7eb; border-radius:12px; background:white; }
      .timetable-grid { min-width:980px; display:grid; gap:0; }
      .tt-head { background:#f3f4f6; font-weight:600; padding:10px; border-bottom:1px solid #e5e7eb; border-right:1px solid #e5e7eb; }
      .tt-cell { min-height:140px; border-right:1px solid #e5e7eb; border-bottom:1px solid #e5e7eb; padding:8px; background:#fff; }
      .tt-rowhead { background:#f9fafb; padding:10px; border-right:1px solid #e5e7eb; border-bottom:1px solid #e5e7eb; min-width:220px; }
      .lesson-block { border:1px solid #bfdbfe; background:#eff6ff; border-radius:10px; padding:8px; margin-bottom:8px; font-size:12px; }
      .lesson-actions { display:flex; flex-wrap:wrap; gap:4px; margin-top:6px; }
      .mini-link { font-size:11px; padding:4px 6px; border-radius:6px; text-decoration:none; background:#dbeafe; color:#1e3a8a; }
      .two-col { display:grid; grid-template-columns:2fr 1fr; gap:14px; }
      .muted { color:#6b7280; font-size:12px; }
      @media (max-width: 1100px) { .two-col { grid-template-columns:1fr; } }
    </style>
    """
    layout = body
    if user:
        lang_options = "".join([
            f"<option value='{code}' {'selected' if lang == code else ''}>{label}</option>"
            for code, label in LANG_LABELS.items()
        ])
        keys = ROLE_MENU_KEYS.get(user["role"], ["dashboard"])
        menu_links = "".join([
            f"<a class='nav-link {'active' if current_menu==k else ''}' href='{NAV_PATHS[k]}?lang={lang}'>{menu_t(k, lang)}</a>"
            for k in keys
        ])
        flash_html = f"<div class='flash {flash_type}'>{flash_msg}</div>" if flash_msg else ""
        layout = f"""
        <div class='app'>
          <aside class='sidebar'>
            <div class='brand'>ReadingTown LMS</div>
            {menu_links}
          </aside>
          <main class='main'>
            <div class='topbar'>
              <div>{menu_t('login_as', lang)}: <strong>{user['name']}</strong> ({role_label(user['role'], lang)})</div>
              <div>
                <span>{menu_t('lang', lang)}:</span>
                <select onchange="window.location.href=window.location.pathname+'?lang='+this.value">{lang_options}</select>
                <a class='btn secondary' href='/logout'>{menu_t('logout', lang)}</a>
              </div>
            </div>
            <h2 class='page-title'>{title}</h2>
            {flash_html}
            {body}
          </main>
        </div>
        """
    else:
        layout = f"<div style='max-width:980px;margin:24px auto'><h2 class='page-title'>{title}</h2>{body}</div>"
    return f"<html><head><meta charset='utf-8'><title>{title}</title>{css}</head><body>{layout}</body></html>".encode("utf-8")
def require_login(environ):
    user = current_user(environ)
    if not user:
        return None, redirect('/login')
    return user, None
def redirect(path):
    return "302 Found", [("Location", path)], b""
def has_role(user, roles):
    return user and user["role"] in roles
def route_allowed(user, route_key):
    if not user:
        return False
    return route_key in ROLE_MENU_KEYS.get(user["role"], [])
def forbidden_html(user, msg=None):
    if msg is None:
        msg = t("common.forbidden")
    html = render_html("403 Forbidden", f"<p style='color:red'>{msg}</p>", user)
    return "403 Forbidden", [("Content-Type", "text/html; charset=utf-8")], html
def forbidden_json(msg=t('common.forbidden')):
    return json_resp({"error": msg}, "403 Forbidden")
def can_view_student_row(user, st):
    if user["role"] in (ROLE_OWNER, ROLE_MANAGER):
        return True
    if user["role"] == ROLE_TEACHER:
        return st["current_class_teacher_id"] == user["id"]
    if user["role"] == ROLE_PARENT:
        return (st["guardian_name"] or "") == user["name"]
    if user["role"] == ROLE_STUDENT:
        return st["user_id"] == user["id"]
    return False
def json_resp(data, status="200 OK"):
    return status, [("Content-Type", "application/json; charset=utf-8")], json.dumps(data, ensure_ascii=False).encode("utf-8")
def text_resp(text, status="200 OK"):
    return status, [("Content-Type", "text/html; charset=utf-8")], text
def fetch_student_candidates(conn, keyword, limit=10):
    kw = (keyword or "").strip()
    if not kw:
        return []
    like = f"%{kw}%"
    return conn.execute(
        """SELECT id, student_no, name_ko, phone FROM students
        WHERE name_ko LIKE ? OR student_no LIKE ? OR phone LIKE ?
        ORDER BY id DESC LIMIT ?""",
        (like, like, like, limit),
    ).fetchall()
def fetch_class_candidates(conn, keyword, limit=10):
    kw = (keyword or "").strip()
    if not kw:
        return []
    like = f"%{kw}%"
    return conn.execute(
        """SELECT c.id, c.name, COALESCE(co.name, '') AS course_name
        FROM classes c
        LEFT JOIN courses co ON co.id=c.course_id
        WHERE c.name LIKE ? OR co.name LIKE ?
        ORDER BY c.id DESC LIMIT ?""",
        (like, like, limit),
    ).fetchall()
def fetch_teacher_candidates(conn, keyword, limit=10):
    kw = (keyword or "").strip()
    if not kw:
        return []
    like = f"%{kw}%"
    return conn.execute(
        """SELECT id, name, username FROM users
        WHERE role='teacher' AND (name LIKE ? OR username LIKE ?)
        ORDER BY id DESC LIMIT ?""",
        (like, like, limit),
    ).fetchall()
def render_picker_block(title, search_name, search_value, selected_name, selected_id, selected_label, candidates, base_path, lang, query_keep=None):
    query_keep = query_keep or {}
    hidden = "".join([f"<input type='hidden' name='{k}' value='{v}'>" for k, v in query_keep.items() if v not in (None, "")])
    cand_rows = ""
    for c in candidates:
        cid = c['id']
        label = c.get('label', '') if isinstance(c, dict) else ''
        if not label:
            if 'student_no' in c.keys():
                label = f"{c['name_ko']} ({c['student_no'] or '-'}, {c['phone'] or '-'})"
            elif 'course_name' in c.keys():
                label = f"{c['name']} / {c['course_name'] or '-'}"
            else:
                label = f"{c['name']} ({c['username']})"
        qp = "&".join([f"{k}={v}" for k, v in query_keep.items() if v not in (None, "")])
        sep = "&" if qp else ""
        cand_rows += f"<li><a href='{base_path}?lang={lang}{sep}{qp}&{selected_name}={cid}'>{label}</a></li>"
    return f"""
    <div class='card'>
      <h4>{title}</h4>
      <form method='get' class='filter-row'>
        <input type='hidden' name='lang' value='{lang}'>
        {hidden}
        <input name='{search_name}' value='{search_value or ''}' placeholder='search'>
        <button>{t("common.search")}</button>
      </form>
      <div style='margin:6px 0'>{t("common.selected")}: <strong>{selected_label or '-'}</strong> (ID: {selected_id or '-'})</div>
      <ul style='margin:0; padding-left:18px'>{cand_rows or f'<li class="empty-msg">{t("common.no_data")}</li>'}</ul>
    </div>
    """
def app(environ, start_response):
    global CURRENT_LANG
    query = parse_query(environ)
    CURRENT_LANG = get_lang(environ)
    _orig_start_response = start_response
    def start_response(status, headers, exc_info=None):
        if query.get("lang", "").strip().lower() in SUPPORTED_LANGS:
            headers.append(("Set-Cookie", f"lang={CURRENT_LANG}; Path=/; Max-Age=31536000"))
        return _orig_start_response(status, headers, exc_info)
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")
    # 인증 API
    if path == "/api/auth/login" and method == "POST":
        data = parse_body(environ)
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password_hash=?",
            (data.get("username", ""), hash_pw(data.get("password", ""))),
        ).fetchone()
        if not user:
            conn.close()
            status, headers, body = json_resp({"error": t('login.failed')}, "401 Unauthorized")
            start_response(status, headers)
            return [body]
        token = str(uuid.uuid4())
        conn.execute("INSERT INTO sessions(user_id, token, created_at) VALUES(?,?,?)", (user["id"], token, now()))
        conn.commit()
        conn.close()
        status, headers, body = json_resp({"message": "ok", "role": user["role"]})
        headers.append(("Set-Cookie", f"session={token}; Path=/; HttpOnly"))
        start_response(status, headers)
        return [body]
    if path == "/login":
        if method == "GET":
            html = render_html(t("login.title"), f"""
            <form method='post'>
              <div>{t('login.username')} <input name='username'></div>
              <div>{t('login.password')} <input name='password' type='password'></div>
              <button type='submit'>{t('common.login')}</button>
            </form>
            <p>{t('login.default_accounts')}</p>
            """)
            status, headers, body = text_resp(html)
            start_response(status, headers)
            return [body]
        data = parse_body(environ)
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password_hash=?",
            (data.get("username", ""), hash_pw(data.get("password", ""))),
        ).fetchone()
        if not user:
            conn.close()
            html = render_html(t("login.title"), f"<p style='color:red'>{t('login.failed')}</p>")
            status, headers, body = text_resp(html, "401 Unauthorized")
            start_response(status, headers)
            return [body]
        token = str(uuid.uuid4())
        conn.execute("INSERT INTO sessions(user_id, token, created_at) VALUES(?,?,?)", (user["id"], token, now()))
        conn.commit()
        conn.close()
        status, headers, body = redirect('/dashboard')
        headers.append(("Set-Cookie", f"session={token}; Path=/; HttpOnly"))
        start_response(status, headers)
        return [body]
    if path == "/logout":
        status, headers, body = redirect('/login')
        headers.append(("Set-Cookie", "session=; Path=/; Max-Age=0"))
        start_response(status, headers)
        return [body]
    if path == "/":
        status, headers, body = redirect('/dashboard')
        start_response(status, headers)
        return [body]
    user, resp = require_login(environ)
    if resp:
        status, headers, body = resp
        start_response(status, headers)
        return [body]
    # Dashboard
    if path == "/dashboard":
        stats = {}
        conn_dash = get_db()
        stats["users"] = conn_dash.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        stats["students"] = conn_dash.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
        stats["classes"] = conn_dash.execute("SELECT COUNT(*) c FROM classes").fetchone()["c"]
        stats["attendance"] = conn_dash.execute("SELECT COUNT(*) c FROM attendance").fetchone()["c"]
        conn_dash.close()
        body_html = f"""
        <div class='card'>
          <h3>{t("dash.stats")}</h3>
          <div class='filter-row'>
            <div class='card' style='min-width:160px'><strong>{t('dash.users')}</strong><div>{stats['users']}</div></div>
            <div class='card' style='min-width:160px'><strong>{t('dash.students')}</strong><div>{stats['students']}</div></div>
            <div class='card' style='min-width:160px'><strong>{t('dash.classes')}</strong><div>{stats['classes']}</div></div>
            <div class='card' style='min-width:160px'><strong>{t('dash.attendance')}</strong><div>{stats['attendance']}</div></div>
          </div>
        </div>
        <div class='card'>
          <h3>{t("dash.quick")}</h3>
          <div class='filter-row'>
            <a class='btn' href='/students?lang={CURRENT_LANG}'>{menu_t('students')}</a>
            <a class='btn' href='/masterdata?lang={CURRENT_LANG}'>{menu_t('masterdata')}</a>
            <a class='btn' href='/schedule?lang={CURRENT_LANG}'>{menu_t('schedule')}</a>
            <a class='btn' href='/attendance?lang={CURRENT_LANG}'>{menu_t('attendance')}</a>
            <a class='btn' href='/homework?lang={CURRENT_LANG}'>{menu_t('homework')}</a>
          </div>
        </div>
        """
        html = render_html(t("dash.title"), body_html, user, current_menu="dashboard")
        status, headers, body = text_resp(html)
        start_response(status, headers)
        return [body]
    conn = get_db()
    # 사용자 관리
    if path == "/users":
        if not has_role(user, [ROLE_OWNER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        flash_msg = ""
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            data = parse_body(environ)
            conn.execute(
                "INSERT INTO users(name, username, password_hash, role, created_at) VALUES(?,?,?,?,?)",
                (data.get("name"), data.get("username"), hash_pw(data.get("password", "1234")), data.get("role"), now()),
            )
            conn.commit()
            flash_msg = t("users.saved")
        users = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
        rows = "".join([
            f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['username']}</td><td><span class='badge'>{ROLE_LABELS.get(u['role'],u['role'])}</span></td></tr>"
            for u in users
        ])
        form = ""
        if has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            form = f"""
            <div class='card'>
              <h3>{t("users.add")}</h3>
              <form method='post' class='filter-row'>
                <label>{t('field.name')} <input name='name'></label>
                <label>{t('login.username')} <input name='username'></label>
                <label>{t('login.password')} <input name='password' type='password'></label>
                <label>{t('field.role')}
                <select name='role'>
                  <option value='owner'>{role_label('owner')}</option><option value='manager'>{role_label('manager')}</option><option value='teacher'>{role_label('teacher')}</option>
                  <option value='parent'>{role_label('parent')}</option><option value='student'>{role_label('student')}</option>
                </select></label>
                <button>{t("common.save")}</button>
              </form>
            </div>
            """
        body_html = form + f"""
        <div class='card'>
          <h3>{t("users.list")}</h3>
          <table>
            <tr><th>{t('field.id')}</th><th>{t('field.name')}</th><th>{t('login.username')}</th><th>{t('field.role')}</th></tr>
            {rows or "<tr><td colspan='4' class='empty-msg'>{t('common.no_data')}</td></tr>"}
          </table>
        </div>
        """
        html = render_html(t("users.page_title"), body_html, user, current_menu="users", flash_msg=flash_msg)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path.startswith("/students/"):
        student_id = path.split("/")[-1]
        if not student_id.isdigit():
            conn.close()
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return ["Not Found".encode("utf-8")]
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            d = parse_body(environ)
            action = d.get("action")
            if action == "save":
                errs = []
                credits = as_float(d.get("remaining_credits") or 0)
                if not (d.get("name_ko") or "").strip():
                    add_error(errs, "name_ko", "필수값입니다")
                if credits is None:
                    add_error(errs, "remaining_credits", "숫자 형식이어야 합니다")
                if (d.get("status") or "active") not in ("active", "leave", "ended"):
                    add_error(errs, "status", "허용되지 않는 상태값입니다")
                class_id_val = d.get("current_class_id") or None
                if class_id_val and not ensure_exists(conn, "classes", class_id_val):
                    add_error(errs, "current_class_id", "존재하지 않는 반입니다")
                for date_field in ["enrolled_at", "leave_start_date", "leave_end_date"]:
                    dv = (d.get(date_field) or "").strip()
                    if dv and not is_valid_date(dv):
                        add_error(errs, date_field, "날짜 형식은 YYYY-MM-DD 여야 합니다")
                if errs:
                    status, headers, body = redirect(f"/students/{student_id}?lang={CURRENT_LANG}&msg=validation_error")
                else:
                    conn.execute(
                        """UPDATE students SET
                        student_no=?, name_ko=?, name_en=?, phone=?, guardian_name=?, guardian_phone=?,
                        current_class_id=?, remaining_credits=?, status=?, enrolled_at=?, leave_start_date=?, leave_end_date=?, memo=?, updated_at=?
                        WHERE id=?""",
                        (
                            d.get("student_no"), d.get("name_ko"), d.get("name_en"), d.get("phone"), d.get("guardian_name"), d.get("guardian_phone"),
                            class_id_val, credits, d.get("status") or "active", d.get("enrolled_at"),
                            d.get("leave_start_date"), d.get("leave_end_date"), d.get("memo"), now(), student_id,
                        ),
                    )
                    conn.commit()
                    status, headers, body = redirect(f"/students/{student_id}?lang={CURRENT_LANG}&msg=saved")
                conn.close()
                start_response(status, headers)
                return [body]
            if action == "password":
                new_password = d.get("new_password", "").strip()
                student_row = conn.execute("SELECT user_id FROM students WHERE id=?", (student_id,)).fetchone()
                if not student_row or not student_row["user_id"]:
                    status, headers, body = redirect(f"/students/{student_id}?lang={CURRENT_LANG}&msg=no_user")
                    conn.close()
                    start_response(status, headers)
                    return [body]
                if not new_password:
                    status, headers, body = redirect(f"/students/{student_id}?lang={CURRENT_LANG}&msg=empty_pw")
                    conn.close()
                    start_response(status, headers)
                    return [body]
                conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_pw(new_password), student_row["user_id"]))
                conn.commit()
                status, headers, body = redirect(f"/students/{student_id}?lang={CURRENT_LANG}&msg=pw_saved")
                conn.close()
                start_response(status, headers)
                return [body]
        student = conn.execute(
            """SELECT s.*, u.username, c.name AS class_name, c.teacher_id AS current_class_teacher_id FROM students s
            LEFT JOIN users u ON u.id=s.user_id
            LEFT JOIN classes c ON c.id=s.current_class_id
            WHERE s.id=?""",
            (student_id,),
        ).fetchone()
        classes = conn.execute("SELECT id, name FROM classes ORDER BY id DESC").fetchall()
        if not student:
            conn.close()
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return ["Student Not Found".encode("utf-8")]
        if not can_view_student_row(user, student):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        msg_key = query.get("msg", "")
        msg_map = {
            "saved": t("students.msg.saved"),
            "validation_error": "입력값 검증에 실패했습니다. 필수값/날짜/참조값을 확인하세요.",
            "pw_saved": t("students.msg.pw_saved"),
            "no_user": t("students.msg.no_user"),
            "empty_pw": t("students.msg.empty_pw"),
        }
        message = msg_map.get(msg_key, "")
        detail_page_size = 10
        def parse_page_param(name):
            raw = query.get(name, "1")
            return int(raw) if raw.isdigit() and int(raw) > 0 else 1
        def fetch_paged(sql, params, page):
            offset = (page - 1) * detail_page_size
            rows = conn.execute(sql + " LIMIT ? OFFSET ?", (*params, detail_page_size + 1, offset)).fetchall()
            has_next = len(rows) > detail_page_size
            return rows[:detail_page_size], has_next
        student_user_id = student["user_id"]
        att_page = parse_page_param("att_page")
        attendance_rows, attendance_has_next = fetch_paged(
            """SELECT a.lesson_date, a.status, a.note, c.name AS class_name
            FROM attendance a LEFT JOIN classes c ON c.id=a.class_id
            WHERE a.student_id=? ORDER BY a.id DESC""",
            (student_user_id,),
            att_page,
        )
        hw_page = parse_page_param("hw_page")
        submission_rows, submission_has_next = fetch_paged(
            """SELECT hs.id, h.title, hs.submitted, hs.submitted_at, hs.feedback
            FROM homework_submissions hs LEFT JOIN homework h ON h.id=hs.homework_id
            WHERE hs.student_id=? ORDER BY hs.id DESC""",
            (student_user_id,),
            hw_page,
        )
        exam_page = parse_page_param("exam_page")
        exam_rows, exam_has_next = fetch_paged(
            """SELECT e.name AS exam_name, es.score, e.exam_date
            FROM exam_scores es LEFT JOIN exams e ON e.id=es.exam_id
            WHERE es.student_id=? ORDER BY es.id DESC""",
            (student_user_id,),
            exam_page,
        )
        counseling_page = parse_page_param("counseling_page")
        counseling_rows, counseling_has_next = fetch_paged(
            """SELECT c.created_at AS recorded_at, c.memo, c.is_special_note
            FROM counseling c WHERE c.student_id=? ORDER BY c.id DESC""",
            (student_user_id,),
            counseling_page,
        )
        payment_page = parse_page_param("payment_page")
        payment_rows, payment_has_next = fetch_paged(
            """SELECT paid_date, amount, package_hours, remaining_classes
            FROM payments WHERE student_id=? ORDER BY id DESC""",
            (student_user_id,),
            payment_page,
        )
        loan_page = parse_page_param("loan_page")
        loan_rows, loan_has_next = fetch_paged(
            """SELECT b.code, b.title, bl.loaned_at, bl.returned_at
            FROM book_loans bl LEFT JOIN books b ON b.id=bl.book_id
            WHERE bl.student_id=? ORDER BY bl.id DESC""",
            (student_user_id,),
            loan_page,
        )
        def rows_html(rows, cols, empty_colspan):
            if not rows:
                return f"<tr><td colspan='{empty_colspan}'>{t('common.no_data')}</td></tr>"
            out = ""
            for r in rows:
                values = []
                for c in cols:
                    v = r[c]
                    if c == "status" and v:
                        v = status_t(v)
                    elif c == "submitted":
                        v = t("common.yes") if str(v) == "1" else t("common.no")
                    elif c == "is_special_note":
                        v = t("common.yes") if str(v) == "1" else t("common.no")
                    if v in (None, ""):
                        v = "-"
                    values.append(f"<td>{v}</td>")
                out += "<tr>" + "".join(values) + "</tr>"
            return out
        def section_pager(param_name, page, has_next):
            page_keys = ["att_page", "hw_page", "exam_page", "counseling_page", "payment_page", "loan_page"]
            def mk_link(target_page):
                qp = {k: query.get(k, "1") for k in page_keys}
                qp[param_name] = str(target_page)
                qp["lang"] = CURRENT_LANG
                qstr = "&".join([f"{k}={v}" for k, v in qp.items()])
                return f"?{qstr}"
            prev_link = f"<a href='{mk_link(page-1)}'>{t('common.prev')}</a>" if page > 1 else ""
            next_link = f"<a href='{mk_link(page+1)}'>{t('common.next')}</a>" if has_next else ""
            if not prev_link and not next_link:
                return ""
            sep = " | " if prev_link and next_link else ""
            return f"<div style='margin:4px 0 12px 0'>{prev_link}{sep}{next_link}</div>"
        class_opts = ["<option value=''>-</option>"]
        for c in classes:
            selected = "selected" if student["current_class_id"] == c["id"] else ""
            class_opts.append(f"<option value='{c['id']}' {selected}>{c['name']}</option>")
        class_options = "".join(class_opts)
        edit_form = ""
        pw_form = ""
        if has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            edit_form = f"""
            <form id='student-edit' method='post' style='margin-bottom:16px'>
              <input type='hidden' name='action' value='save'>
              <h4>{t('common.edit')}</h4>
              {t('students.field.student_no')} <input name='student_no' value='{student['student_no'] or ''}'>
              {t('students.field.name_ko')} <input name='name_ko' value='{student['name_ko'] or ''}'>
              {t('students.field.name_en')} <input name='name_en' value='{student['name_en'] or ''}'><br>
              {t('students.field.phone')} <input name='phone' value='{student['phone'] or ''}'>
              {t('students.field.guardian_name')} <input name='guardian_name' value='{student['guardian_name'] or ''}'>
              {t('students.field.guardian_phone')} <input name='guardian_phone' value='{student['guardian_phone'] or ''}'><br>
              {t('students.field.class')} <select name='current_class_id'>{class_options}</select>
              {t('students.field.credits')} <input name='remaining_credits' value='{student['remaining_credits'] or 0}'>
              {t('students.field.status')} <select name='status'>
                <option value='active' {'selected' if student['status']=='active' else ''}>{status_t('active')}</option>
                <option value='leave' {'selected' if student['status']=='leave' else ''}>{status_t('leave')}</option>
                <option value='ended' {'selected' if student['status']=='ended' else ''}>{status_t('ended')}</option>
              </select><br>
              {t('students.field.enrolled_at')} <input name='enrolled_at' value='{student['enrolled_at'] or ''}'>
              {t('students.field.leave_start_date')} <input name='leave_start_date' value='{student['leave_start_date'] or ''}'>
              {t('students.field.leave_end_date')} <input name='leave_end_date' value='{student['leave_end_date'] or ''}'><br>
              {t('students.field.memo')} <input name='memo' style='width:500px' value='{student['memo'] or ''}'><br>
              <button>{t('common.save')}</button>
            </form>
            """
            pw_form = f"""
            <form method='post'>
              <input type='hidden' name='action' value='password'>
              <h4>{t('students.password_reset')}</h4>
              {t('students.new_password')} <input name='new_password' type='password'>
              <button>{t('common.edit')}</button>
            </form>
            """
        edit_button_html = ""
        if has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            edit_button_html = f'<div style="margin:8px 0"><button type="button" onclick="location.hash=\'student-edit\'">{t("students.detail.edit")}</button></div>'
        body_html = f"""
        <div><a href='/students?lang={CURRENT_LANG}'>← {t("students.detail.back")}</a></div>
        <h3>{student['name_ko']} ({student['student_no'] or '-'})</h3>{edit_button_html}
        <h4>{t('students.detail.section.basic')}</h4>
        <table>
          <tr><th>{t('students.field.student_no')}</th><td>{student['student_no'] or '-'}</td></tr>
          <tr><th>{t('students.field.name_ko')}</th><td>{student['name_ko'] or '-'}</td></tr>
          <tr><th>{t('students.field.name_en')}</th><td>{student['name_en'] or '-'}</td></tr>
          <tr><th>{t('students.field.phone')}</th><td>{student['phone'] or '-'}</td></tr>
          <tr><th>{t('students.field.guardian_name')}</th><td>{student['guardian_name'] or '-'}</td></tr>
          <tr><th>{t('students.field.guardian_phone')}</th><td>{student['guardian_phone'] or '-'}</td></tr>
          <tr><th>{t('students.field.class')}</th><td>{student['class_name'] or '-'}</td></tr>
          <tr><th>{t('students.field.credits')}</th><td>{student['remaining_credits'] or 0}</td></tr>
          <tr><th>{t('students.field.status')}</th><td>{status_t(student['status']) if student['status'] else '-'}</td></tr>
          <tr><th>{t('students.field.enrolled_at')}</th><td>{student['enrolled_at'] or '-'}</td></tr>
          <tr><th>{t('students.field.leave_period')}</th><td>{student['leave_start_date'] or '-'} ~ {student['leave_end_date'] or '-'}</td></tr>
          <tr><th>{t('students.field.memo')}</th><td>{student['memo'] or '-'}</td></tr>
        </table>
        <h4>{t('students.detail.section.attendance')}</h4>
        <table>
          <tr><th>{t('students.field.lesson_date')}</th><th>{t('students.field.class')}</th><th>{t('students.field.status')}</th><th>{t('students.field.note')}</th></tr>
          {rows_html(attendance_rows, ['lesson_date', 'class_name', 'status', 'note'], 4)}
        </table>
        {section_pager('att_page', att_page, attendance_has_next)}
        <h4>{t('students.detail.section.homework')}</h4>
        <table>
          <tr><th>{t('students.field.homework')}</th><th>{t('students.field.submitted')}</th><th>{t('students.field.submitted_at')}</th><th>{t('students.field.feedback')}</th></tr>
          {rows_html(submission_rows, ['title', 'submitted', 'submitted_at', 'feedback'], 4)}
        </table>
        {section_pager('hw_page', hw_page, submission_has_next)}
        <h4>{t('students.detail.section.exams')}</h4>
        <table>
          <tr><th>{t('students.field.exam_name')}</th><th>{t('students.field.score')}</th><th>{t('students.field.exam_date')}</th></tr>
          {rows_html(exam_rows, ['exam_name', 'score', 'exam_date'], 3)}
        </table>
        {section_pager('exam_page', exam_page, exam_has_next)}
        <h4>{t('students.detail.section.counseling')}</h4>
        <table>
          <tr><th>{t('students.field.recorded_at')}</th><th>{t('students.field.memo')}</th><th>{t('students.field.special_note')}</th></tr>
          {rows_html(counseling_rows, ['recorded_at', 'memo', 'is_special_note'], 3)}
        </table>
        {section_pager('counseling_page', counseling_page, counseling_has_next)}
        <h4>{t('students.detail.section.payments')}</h4>
        <table>
          <tr><th>{t('students.field.paid_date')}</th><th>{t('students.field.amount')}</th><th>{t('students.field.package_hours')}</th><th>{t('students.field.remaining_classes')}</th></tr>
          {rows_html(payment_rows, ['paid_date', 'amount', 'package_hours', 'remaining_classes'], 4)}
        </table>
        {section_pager('payment_page', payment_page, payment_has_next)}
        <h4>{t('students.detail.section.loans')}</h4>
        <table>
          <tr><th>{t('students.field.code')}</th><th>{t('students.field.title')}</th><th>{t('students.field.loaned_at')}</th><th>{t('students.field.returned_at')}</th></tr>
          {rows_html(loan_rows, ['code', 'title', 'loaned_at', 'returned_at'], 4)}
        </table>
        {section_pager('loan_page', loan_page, loan_has_next)}
        {edit_form}
        {pw_form}
        """
        html = render_html(t("students.detail.title"), body_html, user, current_menu="students", flash_msg=message)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path == "/students":
        flash_msg = ""
        flash_type = "success"
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            d = parse_body(environ)
            errs = []
            student_user_id = d.get("user_id")
            if not ensure_exists(conn, "users", student_user_id, extra_where="role='student'"):
                add_error(errs, "user_id", "학생 role 사용자만 가능합니다")
            if not (d.get("name_ko") or "").strip():
                add_error(errs, "name_ko", "필수값입니다")
            credits = as_float(d.get("remaining_credits") or 0)
            if credits is None:
                add_error(errs, "remaining_credits", "숫자 형식이어야 합니다")
            status_v = d.get("status") or "active"
            if status_v not in ("active", "leave", "ended"):
                add_error(errs, "status", "허용되지 않는 상태값입니다")
            class_id_val = d.get("current_class_id") or None
            if class_id_val and not ensure_exists(conn, "classes", class_id_val):
                add_error(errs, "current_class_id", "존재하지 않는 반입니다")
            for date_field in ["enrolled_at", "leave_start_date", "leave_end_date"]:
                dv = (d.get(date_field) or "").strip()
                if dv and not is_valid_date(dv):
                    add_error(errs, date_field, "YYYY-MM-DD 형식이어야 합니다")
            if errs:
                flash_msg = format_errors(errs)
                flash_type = "error"
                log_event(conn, "ERROR", path, "학생 저장 검증 실패", "\n".join(errs), user["id"])
            else:
                try:
                    exists = conn.execute("SELECT id FROM students WHERE user_id=?", (student_user_id,)).fetchone()
                    if exists:
                        conn.execute(
                            """UPDATE students SET
                            student_no=?, name_ko=?, name_en=?, phone=?, guardian_name=?, guardian_phone=?,
                            current_class_id=?, remaining_credits=?, status=?, enrolled_at=?, leave_start_date=?, leave_end_date=?, memo=?, updated_at=?
                            WHERE user_id=?""",
                            (
                                d.get("student_no"), d.get("name_ko"), d.get("name_en"), d.get("phone"), d.get("guardian_name"), d.get("guardian_phone"),
                                class_id_val, credits, status_v, d.get("enrolled_at"), d.get("leave_start_date"), d.get("leave_end_date"), d.get("memo"), now(), student_user_id,
                            ),
                        )
                    else:
                        conn.execute(
                            """INSERT INTO students(
                            user_id, student_no, name_ko, name_en, phone, guardian_name, guardian_phone,
                            current_class_id, remaining_credits, status, enrolled_at, leave_start_date, leave_end_date, memo, created_at, updated_at
                            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (
                                student_user_id, d.get("student_no"), d.get("name_ko"), d.get("name_en"), d.get("phone"), d.get("guardian_name"), d.get("guardian_phone"),
                                class_id_val, credits, status_v, d.get("enrolled_at"), d.get("leave_start_date"), d.get("leave_end_date"), d.get("memo"), now(), now(),
                            ),
                        )
                    conn.commit()
                    flash_msg = "저장되었습니다"
                except Exception:
                    conn.rollback()
                    flash_msg = "학생 저장 실패: 입력값 또는 중복값을 확인하세요"
                    flash_type = "error"
                    log_event(conn, "ERROR", path, "학생 저장 예외", traceback.format_exc(), user["id"])
                    conn.commit()
        where = []
        params = []
        q_name = query.get("name", "").strip()
        q_student_no = query.get("student_no", "").strip()
        q_phone = query.get("phone", "").strip()
        if q_name:
            where.append("(s.name_ko LIKE ? OR s.name_en LIKE ?)")
            params += [f"%{q_name}%", f"%{q_name}%"]
        if q_student_no:
            where.append("s.student_no LIKE ?")
            params.append(f"%{q_student_no}%")
        if q_phone:
            where.append("s.phone LIKE ?")
            params.append(f"%{q_phone}%")
        where_sql = ("WHERE " + " AND ".join(where)) if where else ""
        students = conn.execute(
            f"""SELECT s.*, c.name AS class_name, c.teacher_id AS current_class_teacher_id
            FROM students s
            LEFT JOIN classes c ON c.id=s.current_class_id
            {where_sql}
            ORDER BY s.id DESC""",
            params,
        ).fetchall()
        rows = ""
        for st in students:
            if not can_view_student_row(user, st):
                continue
            rows += f"""
            <tr>
              <td>{st['student_no'] or '-'}</td>
              <td><a href='/students/{st['id']}?lang={CURRENT_LANG}'>{st['name_ko'] or '-'}</a></td>
              <td>{st['name_en'] or '-'}</td>
              <td>{st['phone'] or '-'}</td>
              <td>{st['guardian_name'] or '-'}</td>
              <td>{st['guardian_phone'] or '-'}</td>
              <td>{st['class_name'] or '-'}</td>
              <td>{st['remaining_credits'] or 0}</td>
              <td><span class='badge {st['status'] or ''}'>{status_t(st['status']) if st['status'] else '-'}</span></td>
            </tr>
            """
        html = render_html(t('menu.students'), f"""
        <div class='card'>
          <h3>{t("students.search")}</h3>
          <form method='get' class='filter-row'>
            <input type='hidden' name='lang' value='{CURRENT_LANG}'>
            <label>{t('field.name')} <input name='name' value='{q_name}'></label>
            <label>{t('students.field.student_no')} <input name='student_no' value='{q_student_no}'></label>
            <label>{t('students.field.phone')} <input name='phone' value='{q_phone}'></label>
            <button>{t("common.search")}</button>
            <a class='btn secondary' href='/students?lang={CURRENT_LANG}'>{t('common.reset')}</a>
          </form>
        </div>
        <div class='card'>
          <h3>{t("students.list")}</h3>
          <table>
            <tr>
              <th>{t('students.field.student_no')}</th><th>{t('students.field.name_ko')}</th><th>{t('students.field.name_en')}</th><th>{t('students.field.phone')}</th><th>{t('students.field.guardian_name')}</th><th>{t('students.field.guardian_phone')}</th><th>{t('students.field.class')}</th><th>{t('students.field.credits')}</th><th>{t('students.field.status')}</th>
            </tr>
            {rows or "<tr><td colspan='9' class='empty-msg'>{t('common.no_data')}</td></tr>"}
          </table>
        </div>
        """, user, current_menu="students", flash_msg=flash_msg, flash_type=flash_type)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    # 학사 구조
    if path.startswith("/classes/"):
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        class_id = path.split("/")[-1]
        if not class_id.isdigit():
            conn.close()
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return ["Not Found".encode("utf-8")]
        if has_role(user, [ROLE_TEACHER]):
            class_row = conn.execute(
                """SELECT c.*, co.name AS course_name, l.name AS level_name, u.name AS teacher_name
                FROM classes c
                LEFT JOIN courses co ON co.id=c.course_id
                LEFT JOIN levels l ON l.id=c.level_id
                LEFT JOIN users u ON u.id=c.teacher_id
            LEFT JOIN users u2 ON u2.id=sc.teacher_id
                WHERE c.id=? AND c.teacher_id=?""",
                (class_id, user["id"]),
            ).fetchone()
        else:
            class_row = conn.execute(
                """SELECT c.*, co.name AS course_name, l.name AS level_name, u.name AS teacher_name
                FROM classes c
                LEFT JOIN courses co ON co.id=c.course_id
                LEFT JOIN levels l ON l.id=c.level_id
                LEFT JOIN users u ON u.id=c.teacher_id
                WHERE c.id=?""",
                (class_id,),
            ).fetchone()
        if not class_row:
            conn.close()
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return ["Class Not Found".encode("utf-8")]
        student_sort = query.get("student_sort", "name_ko")
        if student_sort not in ("name_ko", "student_no", "status"):
            student_sort = "name_ko"
        student_order = query.get("student_order", "asc").lower()
        if student_order not in ("asc", "desc"):
            student_order = "asc"
        students = conn.execute(
            f"""SELECT id, student_no, name_ko, phone, status
            FROM students WHERE current_class_id=?
            ORDER BY {student_sort} {student_order}, id DESC""",
            (class_id,),
        ).fetchall()
        schedules = conn.execute(
            """SELECT id, day_of_week, start_time, end_time, COALESCE(classroom,'-') AS classroom, COALESCE(status,'active') AS status, COALESCE(note,'') AS note
            FROM schedules WHERE class_id=? ORDER BY id DESC""",
            (class_id,),
        ).fetchall()
        attendance_rows = conn.execute(
            """SELECT a.lesson_date, s.name_ko AS student_name, a.status, a.note
            FROM attendance a LEFT JOIN students s ON s.user_id=a.student_id
            WHERE a.class_id=? ORDER BY a.id DESC LIMIT 20""",
            (class_id,),
        ).fetchall()
        homework_rows = conn.execute(
            """SELECT h.title, h.due_date,
            COUNT(hs.id) AS total_submissions,
            SUM(CASE WHEN hs.submitted=1 THEN 1 ELSE 0 END) AS submitted_count
            FROM homework h
            LEFT JOIN homework_submissions hs ON hs.homework_id=h.id
            WHERE h.class_id=?
            GROUP BY h.id
            ORDER BY h.id DESC LIMIT 20""",
            (class_id,),
        ).fetchall()
        exam_rows = conn.execute(
            """SELECT e.name AS exam_name, e.exam_date, ROUND(AVG(es.score),2) AS avg_score, COUNT(es.id) AS score_count
            FROM exams e
            LEFT JOIN exam_scores es ON es.exam_id=e.id
            WHERE e.class_id=?
            GROUP BY e.id
            ORDER BY e.id DESC LIMIT 20""",
            (class_id,),
        ).fetchall()
        export = query.get("export", "")
        if export in ("students_csv", "attendance_csv"):
            if export == "students_csv":
                lines = ["student_no,name_ko,phone,status"]
                for r in students:
                    lines.append(f'"{r["student_no"] or ""}","{r["name_ko"] or ""}","{r["phone"] or ""}","{r["status"] or ""}"')
                filename = f"class_{class_id}_students.csv"
            else:
                lines = ["lesson_date,student_name,status,note"]
                for r in attendance_rows:
                    lines.append(f'"{r["lesson_date"] or ""}","{r["student_name"] or ""}","{r["status"] or ""}","{r["note"] or ""}"')
                filename = f"class_{class_id}_attendance.csv"
            conn.close()
            start_response("200 OK", [
                ("Content-Type", "text/csv; charset=utf-8"),
                ("Content-Disposition", f"attachment; filename={filename}"),
            ])
            return ["\n".join(lines).encode("utf-8")]
        def rows_html(rows, cols):
            if not rows:
                return f"<tr><td colspan='{len(cols)}'>{t('common.no_data')}</td></tr>"
            out = ""
            for r in rows:
                out += "<tr>" + "".join([f"<td>{r[c] if r[c] not in (None, '') else '-'}</td>" for c in cols]) + "</tr>"
            return out
        student_rows = rows_html(students, ["student_no", "name_ko", "phone", "status"])
        schedule_rows = ""
        if not schedules:
            schedule_rows = f"<tr><td colspan='5' class='empty-msg'>{t('common.no_data')}</td></tr>"
        else:
            for r in sorted(schedules, key=lambda x: (day_sort_value(x['day_of_week']), x['start_time'] or '')):
                schedule_rows += f"<tr><td>{r['day_of_week'] or '-'}</td><td>{r['start_time'] or '-'} ~ {r['end_time'] or '-'}</td><td>{r['classroom'] or '-'}</td><td><span class='badge {r['status'] or ''}'>{status_t(r['status']) if r['status'] else '-'}</span></td><td>{r['note'] or '-'}</td></tr>"
        attendance_html = rows_html(attendance_rows, ["lesson_date", "student_name", "status", "note"])
        homework_html = rows_html(homework_rows, ["title", "due_date", "submitted_count", "total_submissions"])
        exam_html = rows_html(exam_rows, ["exam_name", "exam_date", "avg_score", "score_count"])
        next_order = "desc" if student_order == "asc" else "asc"
        html = render_html(t('academics.class_detail.title'), f"""
        <div class='card'>
        <div><a href='/masterdata?lang={CURRENT_LANG}'>← {t('academics.back_to_list')}</a></div>
        <h3>{class_row['name']}</h3>
        <table>
          <tr><th>{t('academics.basic_info')}</th><td>{t('academics.class_name')}: {class_row['name']}</td></tr>
          <tr><th>{t('academics.course_level')}</th><td>{class_row['course_name'] or '-'} / {class_row['level_name'] or '-'}</td></tr>
          <tr><th>{t('academics.teacher')}</th><td>{class_row['teacher_name'] or '-'}</td></tr>
          <tr><th>{t('academics.student_count')}</th><td>{len(students)}</td></tr>
        </table>
        </div>
        <div class='card'>
        <h4>{t('academics.students')}</h4>
        <div style='margin-bottom:8px'>
          {t('academics.sort')}: {student_sort} ({student_order}) |
          <a href='?lang={CURRENT_LANG}&student_sort=name_ko&student_order={next_order}'>{t('academics.sort_name')}</a> |
          <a href='?lang={CURRENT_LANG}&student_sort=student_no&student_order={next_order}'>{t('academics.sort_student_no')}</a> |
          <a href='?lang={CURRENT_LANG}&student_sort=status&student_order={next_order}'>{t('academics.sort_status')}</a> |
          <a href='?lang={CURRENT_LANG}&student_sort={student_sort}&student_order={student_order}&export=students_csv'>{t('academics.export_students_csv')}</a>
        </div>
        <table>
          <tr><th>{t('students.field.student_no')}</th><th>{t('field.name')}</th><th>{t('students.field.phone')}</th><th>{t('field.status')}</th></tr>
          {student_rows}
        </table>
        </div>
        <div class='card'>
        <h4>{t('academics.schedule')}</h4>
        <table>
          <tr><th>{t('academics.day_of_week')}</th><th>{t('academics.time_slot')}</th><th>{t('academics.classroom')}</th><th>{t('academics.status')}</th><th>{t('field.note')}</th></tr>
          {schedule_rows}
        </table>
        </div>
        <div class='card'>
        <h4>{t('academics.recent_attendance')}</h4>
        <div style='margin-bottom:8px'>
          <a href='?lang={CURRENT_LANG}&student_sort={student_sort}&student_order={student_order}&export=attendance_csv'>{t('academics.export_attendance_csv')}</a>
        </div>
        <table>
          <tr><th>{t('field.date')}</th><th>{t('field.student')}</th><th>{t('field.status')}</th><th>{t('field.note')}</th></tr>
          {attendance_html}
        </table>
        </div>
        <div class='card'>
        <h4>{t('academics.recent_homework')}</h4>
        <table>
          <tr><th>{t('field.homework_title')}</th><th>{t('field.due_date')}</th><th>{t('field.submission_count')}</th><th>{t('field.total_targets')}</th></tr>
          {homework_html}
        </table>
        </div>
        <div class='card'>
        <h4>{t('academics.recent_exams')}</h4>
        <table>
          <tr><th>{t('field.exam_name')}</th><th>{t('field.exam_date')}</th><th>{t('field.avg_score')}</th><th>{t('field.score_entries')}</th></tr>
          {exam_html}
        </table>
        </div>
        """, user, current_menu="masterdata")
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path == "/academics":
        status, headers, body = redirect(f"/schedule?lang={CURRENT_LANG}")
        start_response(status, headers)
        return [body]

    if path == "/masterdata":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        flash_msg = ""
        flash_type = "success"
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            data = parse_body(environ)
            typ = data.get("type")
            errs = []
            try:
                if typ == "course":
                    if not (data.get("name") or "").strip():
                        add_error(errs, "course.name", "필수값입니다")
                    else:
                        conn.execute("INSERT INTO courses(name, created_at) VALUES(?,?)", (data.get("name").strip(), now()))
                elif typ == "level":
                    if not ensure_exists(conn, "courses", data.get("course_id")):
                        add_error(errs, "level.course_id", "존재하지 않는 코스입니다")
                    if not (data.get("name") or "").strip():
                        add_error(errs, "level.name", "필수값입니다")
                    if not errs:
                        conn.execute("INSERT INTO levels(course_id, name, created_at) VALUES(?,?,?)", (data.get("course_id"), data.get("name").strip(), now()))
                elif typ == "class":
                    if not ensure_exists(conn, "courses", data.get("course_id")):
                        add_error(errs, "class.course_id", "존재하지 않는 코스입니다")
                    if data.get("level_id") and not ensure_exists(conn, "levels", data.get("level_id")):
                        add_error(errs, "class.level_id", "존재하지 않는 레벨입니다")
                    if data.get("teacher_id") and not ensure_exists(conn, "users", data.get("teacher_id"), extra_where="role='teacher'"):
                        add_error(errs, "class.teacher_id", "존재하지 않는 강사입니다")
                    if not (data.get("name") or "").strip():
                        add_error(errs, "class.name", "필수값입니다")
                    if not errs:
                        conn.execute("INSERT INTO classes(course_id, level_id, name, teacher_id, created_at) VALUES(?,?,?,?,?)", (data.get("course_id"), data.get("level_id") or None, data.get("name").strip(), data.get("teacher_id") or None, now()))
                elif typ == "classroom":
                    room_name = (data.get("name") or "").strip()
                    if not room_name:
                        add_error(errs, "classroom.name", "필수값입니다")
                    else:
                        conn.execute("INSERT OR IGNORE INTO classrooms(name, room_name, room_code, status, created_at) VALUES(?,?,?,?,?)", (room_name, room_name, room_name, "active", now()))
                elif typ == "time_slot":
                    st = (data.get("start_time") or "").strip()
                    et = (data.get("end_time") or "").strip()
                    if not st or not et or parse_hhmm(st) is None or parse_hhmm(et) is None:
                        add_error(errs, "time_slot", "시작/종료 시간을 HH:MM 형식으로 입력하세요")
                    elif parse_hhmm(et) <= parse_hhmm(st):
                        add_error(errs, "time_slot", "종료시간은 시작시간보다 커야 합니다")
                    else:
                        label = f"{st}~{et}"
                        conn.execute("INSERT OR IGNORE INTO time_slots(label, start_time, end_time, created_at) VALUES(?,?,?,?)", (label, st, et, now()))
                elif typ in ("delete_course", "delete_level", "delete_class", "delete_classroom", "delete_time_slot"):
                    del_id = data.get("id")
                    table_map = {"delete_course": "courses", "delete_level": "levels", "delete_class": "classes", "delete_classroom": "classrooms", "delete_time_slot": "time_slots"}
                    table = table_map[typ]
                    if not ensure_exists(conn, table, del_id):
                        add_error(errs, "delete.id", "삭제할 데이터가 없습니다")
                    elif table == "courses" and conn.execute("SELECT 1 FROM classes WHERE course_id=? LIMIT 1", (del_id,)).fetchone():
                        add_error(errs, "course", "반에서 사용 중인 코스는 삭제할 수 없습니다")
                    elif table == "levels" and conn.execute("SELECT 1 FROM classes WHERE level_id=? LIMIT 1", (del_id,)).fetchone():
                        add_error(errs, "level", "반에서 사용 중인 레벨은 삭제할 수 없습니다")
                    elif table == "classes" and conn.execute("SELECT 1 FROM schedules WHERE class_id=? LIMIT 1", (del_id,)).fetchone():
                        add_error(errs, "class", "시간표에서 사용 중인 반은 삭제할 수 없습니다")
                    if not errs:
                        conn.execute(f"DELETE FROM {table} WHERE id=?", (del_id,))
                if errs:
                    flash_msg = format_errors(errs)
                    flash_type = "error"
                    log_event(conn, "ERROR", path, "마스터데이터 검증 실패", "\n".join(errs), user["id"])
                else:
                    conn.commit()
                    flash_msg = "삭제되었습니다" if str(typ).startswith("delete_") else t("common.save")
            except Exception:
                conn.rollback()
                flash_msg = "저장/삭제 처리 중 오류가 발생했습니다"
                flash_type = "error"
                log_event(conn, "ERROR", path, "마스터데이터 예외", traceback.format_exc(), user["id"])
                conn.commit()

        courses = conn.execute("SELECT id, name, created_at FROM courses ORDER BY id DESC").fetchall()
        levels = conn.execute("""SELECT l.id, l.name, c.name AS course_name, l.course_id, l.created_at
                               FROM levels l LEFT JOIN courses c ON c.id=l.course_id ORDER BY l.id DESC""").fetchall()
        classes = conn.execute("""SELECT c.id, c.name, c.teacher_id, co.name AS course_name, l.name AS level_name, u.name AS teacher_name,
                (SELECT COUNT(*) FROM students s WHERE s.current_class_id=c.id) AS student_count
                FROM classes c
                LEFT JOIN courses co ON co.id=c.course_id
                LEFT JOIN levels l ON l.id=c.level_id
                LEFT JOIN users u ON u.id=c.teacher_id
                ORDER BY c.id DESC""").fetchall()
        teachers = conn.execute("SELECT id, name, username FROM users WHERE role='teacher' ORDER BY id DESC").fetchall()
        classrooms = conn.execute("SELECT id, name, created_at FROM classrooms ORDER BY id DESC").fetchall()
        time_slots = conn.execute("SELECT id, label, start_time, end_time, created_at FROM time_slots ORDER BY id DESC").fetchall()

        teacher_options = "".join([f"<option value='{tr['id']}'>{tr['name']} ({tr['username']})</option>" for tr in teachers])

        def rows_html(rows, cols):
            if not rows:
                return f"<tr><td colspan='{len(cols)}' class='empty-msg'>{t('common.no_data')}</td></tr>"
            out = ""
            for r in rows:
                out += "<tr>" + "".join([f"<td>{r[c] if r[c] not in (None, '') else '-'}</td>" for c in cols]) + "</tr>"
            return out

        html = render_html(t('menu.masterdata'), f"""
        <div class='card'><h4>{t('menu.masterdata')}</h4><div class='muted'>{t('academics.go_structure')}</div></div>
        <div class='card'>
          <h4>{t('academics.register')}</h4>
          <form method='post' class='filter-row'><input type='hidden' name='type' value='course'><label>{t('academics.course_name')} <input name='name'></label><button>{t('common.add')}</button></form>
          <form method='post' class='filter-row'><input type='hidden' name='type' value='level'><label>{t('academics.level_name')} <input name='name'></label><label>{t('academics.course_id')} <input name='course_id'></label><button>{t('common.add')}</button></form>
          <form method='post' class='filter-row'><input type='hidden' name='type' value='class'><label>{t('academics.class_name')} <input name='name'></label><label>{t('academics.course_id')} <input name='course_id'></label><label>{t('academics.level_id')} <input name='level_id'></label><label>{t('academics.teacher')} <select name='teacher_id'><option value=''>-</option>{teacher_options}</select></label><button>{t('common.add')}</button></form>
          <form method='post' class='filter-row'><input type='hidden' name='type' value='classroom'><label>{t('academics.classroom')} <input name='name'></label><button>{t('common.add')}</button></form>
          <form method='post' class='filter-row'><input type='hidden' name='type' value='time_slot'><label>{t('academics.start_time')} <input type='time' name='start_time'></label><label>{t('academics.end_time')} <input type='time' name='end_time'></label><button>{t('common.add')}</button></form>
        </div>
        <div class='card'><h4>{t('academics.class_list')}</h4><table><tr><th>{t('academics.class_name')}</th><th>{t('academics.course')}</th><th>{t('academics.level')}</th><th>{t('academics.teacher')}</th><th>{t('academics.student_count')}</th><th>{t('common.delete')}</th></tr>{''.join([f"<tr><td><a href='/classes/{c['id']}?lang={CURRENT_LANG}'>{c['name']}</a></td><td>{c['course_name'] or '-'}</td><td>{c['level_name'] or '-'}</td><td>{c['teacher_name'] or '-'}</td><td>{c['student_count'] or 0}</td><td><form method='post'><input type='hidden' name='type' value='delete_class'><input type='hidden' name='id' value='{c['id']}'><button class='btn secondary'>{t('common.delete')}</button></form></td></tr>" for c in classes]) or f"<tr><td colspan='6' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        <div class='card'><h4>{t('academics.course')}</h4><table><tr><th>{t('field.id')}</th><th>{t('academics.course_name')}</th><th>{t('field.created_at')}</th><th>{t('common.delete')}</th></tr>{''.join([f"<tr><td>{r['id']}</td><td>{r['name']}</td><td>{r['created_at']}</td><td><form method='post'><input type='hidden' name='type' value='delete_course'><input type='hidden' name='id' value='{r['id']}'><button class='btn secondary'>{t('common.delete')}</button></form></td></tr>" for r in courses]) or f"<tr><td colspan='4' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        <div class='card'><h4>{t('academics.level')}</h4><table><tr><th>{t('field.id')}</th><th>{t('academics.level_name')}</th><th>{t('academics.course')}</th><th>{t('field.created_at')}</th><th>{t('common.delete')}</th></tr>{''.join([f"<tr><td>{r['id']}</td><td>{r['name']}</td><td>{r['course_name'] or '-'}</td><td>{r['created_at']}</td><td><form method='post'><input type='hidden' name='type' value='delete_level'><input type='hidden' name='id' value='{r['id']}'><button class='btn secondary'>{t('common.delete')}</button></form></td></tr>" for r in levels]) or f"<tr><td colspan='5' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        <div class='card'><h4>{t('academics.teacher')}</h4><table><tr><th>{t('field.id')}</th><th>{t('field.name')}</th><th>{t('login.username')}</th></tr>{rows_html(teachers,['id','name','username'])}</table></div>
        <div class='card'><h4>{t('academics.classroom')}</h4><table><tr><th>{t('field.id')}</th><th>{t('academics.classroom')}</th><th>{t('field.created_at')}</th><th>{t('common.delete')}</th></tr>{''.join([f"<tr><td>{r['id']}</td><td>{r['name'] or '-'}</td><td>{r['created_at']}</td><td><form method='post'><input type='hidden' name='type' value='delete_classroom'><input type='hidden' name='id' value='{r['id']}'><button class='btn secondary'>{t('common.delete')}</button></form></td></tr>" for r in classrooms]) or f"<tr><td colspan='4' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        <div class='card'><h4>{t('academics.time_slot')}</h4><table><tr><th>{t('field.id')}</th><th>{t('academics.time_slot')}</th><th>{t('academics.start_time')}</th><th>{t('academics.end_time')}</th><th>{t('field.created_at')}</th><th>{t('common.delete')}</th></tr>{''.join([f"<tr><td>{r['id']}</td><td>{r['label']}</td><td>{r['start_time']}</td><td>{r['end_time']}</td><td>{r['created_at']}</td><td><form method='post'><input type='hidden' name='type' value='delete_time_slot'><input type='hidden' name='id' value='{r['id']}'><button class='btn secondary'>{t('common.delete')}</button></form></td></tr>" for r in time_slots]) or f"<tr><td colspan='6' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        """, user, current_menu="masterdata", flash_msg=flash_msg, flash_type=flash_type)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path == "/schedule":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]

        week_offset = safe_int(query.get("week", "0"), 0)
        selected_day = query.get("day", "")
        selected_teacher_id = query.get("teacher_id", "")
        selected_room = query.get("classroom", "").strip()
        selected_course_level = query.get("course_level", "")
        selected_class_q = query.get("class_q", "").strip()
        selected_schedule_id = query.get("schedule_id", "")
        selected_form_class_id = query.get("selected_form_class_id", "")

        flash_msg = ""
        flash_type = "success"

        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            data = parse_body(environ)
            typ = data.get("type")
            if typ == "course":
                conn.execute("INSERT INTO courses(name, created_at) VALUES(?,?)", (data.get("name"), now()))
                conn.commit()
            elif typ == "level":
                conn.execute("INSERT INTO levels(course_id, name, created_at) VALUES(?,?,?)", (data.get("course_id"), data.get("name"), now()))
                conn.commit()
            elif typ == "class":
                conn.execute("INSERT INTO classes(course_id, level_id, name, teacher_id, created_at) VALUES(?,?,?,?,?)", (data.get("course_id"), data.get("level_id"), data.get("name"), data.get("teacher_id"), now()))
                conn.commit()
            elif typ == "schedule":
                schedule_id = data.get("schedule_id", "").strip()
                class_id = (data.get("class_id") or data.get("selected_form_class_id") or "").strip()
                day_of_week = (data.get("day_of_week") or "").strip()
                start_time = (data.get("start_time") or "").strip()
                end_time = (data.get("end_time") or "").strip()
                classroom = (data.get("classroom") or "").strip()
                sc_status = (data.get("status") or "active").strip() or "active"
                note = (data.get("note") or "").strip()

                if not class_id:
                    flash_msg = "class_id: 반을 먼저 선택하세요"
                    flash_type = "error"
                elif not ensure_exists(conn, "classes", class_id):
                    flash_msg = "class_id: 존재하지 않는 반입니다"
                    flash_type = "error"
                elif teacher_id and not ensure_exists(conn, "users", teacher_id, extra_where="role='teacher'"):
                    flash_msg = "teacher_id: 존재하지 않는 강사입니다"
                    flash_type = "error"
                elif classroom and not ensure_exists(conn, "classrooms", classroom, field="name") and not ensure_exists(conn, "classrooms", classroom, field="room_name"):
                    flash_msg = "classroom: 등록된 교실만 선택할 수 있습니다"
                    flash_type = "error"
                elif day_of_week not in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"):
                    flash_msg = "day_of_week: 허용되지 않는 요일 값입니다"
                    flash_type = "error"
                elif not start_time or not end_time or parse_hhmm(start_time) is None or parse_hhmm(end_time) is None:
                    flash_msg = "start_time/end_time: HH:MM 형식으로 선택하세요"
                    flash_type = "error"
                elif parse_hhmm(end_time) is not None and parse_hhmm(start_time) is not None and parse_hhmm(end_time) <= parse_hhmm(start_time):
                    flash_msg = t("academics.validation_end_before_start")
                    flash_type = "error"
                else:
                    class_row = conn.execute("SELECT id, teacher_id FROM classes WHERE id=?", (class_id,)).fetchone()
                    class_teacher_id = class_row["teacher_id"] if class_row else None
                    selected_teacher = (data.get("teacher_id") or "").strip()
                    teacher_id = selected_teacher if selected_teacher else class_teacher_id
                    ignore_id = schedule_id if str(schedule_id).isdigit() else "0"
                    existing = conn.execute(
                        """SELECT sc.*, c.teacher_id AS cls_teacher_id
                        FROM schedules sc LEFT JOIN classes c ON c.id=sc.class_id
                        WHERE sc.day_of_week=? AND sc.id<>?""",
                        (day_of_week, ignore_id),
                    ).fetchall()
                    conflict = None
                    for ex in existing:
                        if not is_time_overlap(start_time, end_time, ex["start_time"], ex["end_time"]):
                            continue
                        if str(ex["class_id"]) == str(class_id):
                            conflict = t("academics.validation_conflict_class")
                            break
                        ex_teacher_id = ex["teacher_id"] or ex["cls_teacher_id"]
                        if teacher_id and ex_teacher_id and str(ex_teacher_id) == str(teacher_id):
                            conflict = t("academics.validation_conflict_teacher")
                            break
                        if classroom and ex["classroom"] and ex["classroom"].strip().lower() == classroom.lower():
                            conflict = t("academics.validation_conflict_room")
                            break
                    if conflict:
                        flash_msg = conflict
                        flash_type = "error"
                        log_event(conn, "ERROR", path, "시간표 중복 검증 실패", conflict, user["id"])
                    else:
                        if str(schedule_id).isdigit():
                            conn.execute(
                                """UPDATE schedules SET class_id=?, day_of_week=?, start_time=?, end_time=?, classroom=?, status=?, note=?, teacher_id=?
                                WHERE id=?""",
                                (class_id, day_of_week, start_time, end_time, classroom or None, sc_status, note or None, teacher_id, schedule_id),
                            )
                            flash_msg = t("academics.updated")
                        else:
                            conn.execute(
                                """INSERT INTO schedules(class_id, day_of_week, start_time, end_time, classroom, status, note, teacher_id, created_at)
                                VALUES(?,?,?,?,?,?,?,?,?)""",
                                (class_id, day_of_week, start_time, end_time, classroom or None, sc_status, note or None, teacher_id, now()),
                            )
                            flash_msg = t("academics.saved")
                        conn.commit()
            if flash_type == "error" and flash_msg:
                log_event(conn, "ERROR", path, "시간표 저장 실패", flash_msg, user["id"])

        courses = conn.execute("SELECT id, name, created_at FROM courses ORDER BY id DESC").fetchall()
        levels = conn.execute("""SELECT l.id, l.name, l.course_id, c.name AS course_name, l.created_at
                               FROM levels l LEFT JOIN courses c ON c.id=l.course_id
                               ORDER BY l.id DESC""").fetchall()
        if has_role(user, [ROLE_TEACHER]):
            classes = conn.execute(
                """SELECT c.id, c.name, c.teacher_id, co.name AS course_name, l.name AS level_name, u.name AS teacher_name,
                (SELECT COUNT(*) FROM students s WHERE s.current_class_id=c.id) AS student_count
                FROM classes c
                LEFT JOIN courses co ON co.id=c.course_id
                LEFT JOIN levels l ON l.id=c.level_id
                LEFT JOIN users u ON u.id=c.teacher_id
                WHERE c.teacher_id=?
                ORDER BY c.id DESC""",
                (user["id"],),
            ).fetchall()
        else:
            classes = conn.execute(
                """SELECT c.id, c.name, c.teacher_id, co.name AS course_name, l.name AS level_name, u.name AS teacher_name,
                (SELECT COUNT(*) FROM students s WHERE s.current_class_id=c.id) AS student_count
                FROM classes c
                LEFT JOIN courses co ON co.id=c.course_id
                LEFT JOIN levels l ON l.id=c.level_id
                LEFT JOIN users u ON u.id=c.teacher_id
                ORDER BY c.id DESC"""
            ).fetchall()

        class_ids = [str(c["id"]) for c in classes]
        if class_ids:
            schedule_sql = f"""SELECT sc.id, sc.class_id, c.name AS class_name, c.teacher_id AS class_teacher_id, sc.teacher_id, COALESCE(u2.name,u.name) AS teacher_name,
            co.name AS course_name, l.name AS level_name, sc.day_of_week, sc.start_time, sc.end_time,
            COALESCE(sc.classroom,'') AS classroom, COALESCE(sc.status,'active') AS status, COALESCE(sc.note,'') AS note,
            (SELECT COUNT(*) FROM students s WHERE s.current_class_id=sc.class_id) AS student_count,
            (SELECT GROUP_CONCAT(name_ko, ', ') FROM (SELECT name_ko FROM students s2 WHERE s2.current_class_id=sc.class_id ORDER BY s2.id LIMIT 2)) AS sample_students
            FROM schedules sc
            LEFT JOIN classes c ON c.id=sc.class_id
            LEFT JOIN users u ON u.id=c.teacher_id
            LEFT JOIN courses co ON co.id=c.course_id
            LEFT JOIN levels l ON l.id=c.level_id
            WHERE sc.class_id IN ({','.join(['?']*len(class_ids))})"""
            schedules = conn.execute(schedule_sql, class_ids).fetchall()
        else:
            schedules = []

        if selected_day:
            schedules = [r for r in schedules if (r["day_of_week"] or "") == selected_day]
        if selected_teacher_id:
            schedules = [r for r in schedules if str(r["teacher_id"] or "") == selected_teacher_id]
        if selected_room:
            schedules = [r for r in schedules if selected_room.lower() in (r["classroom"] or "").lower()]
        if selected_course_level:
            schedules = [r for r in schedules if selected_course_level in [str(r["course_name"] or ""), str(r["level_name"] or "")]]
        if selected_class_q:
            ql = selected_class_q.lower()
            schedules = [r for r in schedules if ql in (r["class_name"] or "").lower()]

        if has_role(user, [ROLE_TEACHER]):
            teacher_rows = [user]
        else:
            teacher_rows = conn.execute("SELECT id, name FROM users WHERE role='teacher' ORDER BY id DESC").fetchall()

        day_values = sorted({(r["day_of_week"] or "").strip() for r in schedules if (r["day_of_week"] or "").strip()}, key=day_sort_value)
        time_slots = sorted({f"{r['start_time']}~{r['end_time']}" for r in schedules if r['start_time'] and r['end_time']})
        if not time_slots:
            time_slots = ["16:25~17:20", "17:25~18:20", "18:30~19:25", "19:35~20:30"]

        if not day_values:
            day_values = ["Mon", "Tue", "Wed", "Thu", "Fri"]

        grouped = {}
        for r in schedules:
            slot = f"{r['start_time']}~{r['end_time']}"
            rowkey = f"{r['teacher_id'] or ''}|{r['classroom'] or '-'}"
            grouped.setdefault((rowkey, slot), []).append(r)

        row_headers = []
        for trow in teacher_rows:
            tname = trow["name"]
            rooms = sorted({(r["classroom"] or "-") for r in schedules if str(r["teacher_id"] or "") == str(trow["id"])}) or ["-"]
            for room in rooms:
                row_headers.append((f"{trow['id']}|{room}", tname, room))

        selected_schedule = None
        if str(selected_schedule_id).isdigit():
            for r in schedules:
                if str(r["id"]) == selected_schedule_id:
                    selected_schedule = r
                    break

        class_rows = ""
        if classes:
            for c in classes:
                class_rows += f"""
                <tr>
                  <td><a href='/classes/{c['id']}?lang={CURRENT_LANG}'>{c['name']}</a></td>
                  <td>{c['course_name'] or '-'}</td>
                  <td>{c['level_name'] or '-'}</td>
                  <td>{c['teacher_name'] or '-'}</td>
                  <td>{c['student_count'] or 0}</td>
                </tr>
                """
        else:
            class_rows = f"<tr><td colspan='5' class='empty-msg'>{t('common.no_data')}</td></tr>"

        def rows_html(rows, cols):
            if not rows:
                return f"<tr><td colspan='{len(cols)}'>{t('common.no_data')}</td></tr>"
            out = ""
            for r in rows:
                out += "<tr>" + "".join([f"<td>{r[c] if r[c] not in (None, '') else '-'}</td>" for c in cols]) + "</tr>"
            return out

        course_rows = rows_html(courses, ["id", "name", "created_at"])
        level_rows = rows_html(levels, ["id", "name", "course_name", "created_at"])

        timetable_cols = ["<div class='tt-head'>" + t("academics.teacher_room") + "</div>"] + [f"<div class='tt-head'>{slot}</div>" for slot in time_slots]
        timetable_cells = ""
        for rowkey, tname, room in row_headers:
            timetable_cells += f"<div class='tt-rowhead'><strong>{tname}</strong><div class='muted'>{t('academics.classroom')}: {room}</div></div>"
            for slot in time_slots:
                lessons = grouped.get((rowkey, slot), [])
                blocks = ""
                for les in lessons:
                    students_label = f"{t('academics.students_summary')} {les['student_count'] or 0}"
                    sample = (les['sample_students'] or '').strip()
                    if sample:
                        students_label += f" ({sample}{' ' + t('academics.more_students') if (les['student_count'] or 0) > 2 else ''})"
                    blocks += f"""
                    <div class='lesson-block'>
                      <div><strong>{les['class_name'] or '-'}</strong></div>
                      <div class='muted'>{les['course_name'] or '-'} / {les['level_name'] or '-'} · {les['teacher_name'] or '-'}</div>
                      <div class='muted'>{les['day_of_week'] or '-'} {les['start_time'] or '-'}~{les['end_time'] or '-'}</div>
                      <div class='muted'>{students_label}</div>
                      <div><span class='badge {les['status'] or ''}'>{status_t(les['status']) if les['status'] else '-'}</span></div>
                      <div class='lesson-actions'>
                        <a class='mini-link' href='/classes/{les['class_id']}?lang={CURRENT_LANG}'>{t('academics.view_class')}</a>
                        <a class='mini-link' href='/attendance?lang={CURRENT_LANG}&selected_class_id={les['class_id']}'>{t('academics.go_attendance')}</a>
                        <a class='mini-link' href='/homework?lang={CURRENT_LANG}&selected_class_id={les['class_id']}'>{t('academics.go_homework')}</a>
                        <a class='mini-link' href='/exams?lang={CURRENT_LANG}&selected_class_id={les['class_id']}'>{t('academics.go_exams')}</a>
                        <a class='mini-link' href='/schedule?lang={CURRENT_LANG}&schedule_id={les['id']}&week={week_offset}'>{t('common.edit')}</a>
                      </div>
                    </div>
                    """
                if not blocks:
                    blocks = f"<div class='empty-msg'>{t('common.no_data')}</div>"
                timetable_cells += f"<div class='tt-cell'>{blocks}</div>"

        week_label = f"W{week_offset:+d}" if week_offset else "W0"
        selected_teacher_options = [f"<option value=''>{t('academics.day_all')}</option>"]
        for tr in teacher_rows:
            selected = "selected" if str(tr["id"]) == selected_teacher_id else ""
            selected_teacher_options.append(f"<option value='{tr['id']}' {selected}>{tr['name']}</option>")

        day_options = [f"<option value=''>{t('academics.day_all')}</option>"]
        for d in sorted({(r['day_of_week'] or '').strip() for r in schedules if (r['day_of_week'] or '').strip()}, key=day_sort_value):
            sel = "selected" if d == selected_day else ""
            day_options.append(f"<option value='{d}' {sel}>{d}</option>")

        course_level_values = sorted({x for r in schedules for x in [r['course_name'] or '', r['level_name'] or ''] if x})
        cl_options = [f"<option value=''>{t('academics.day_all')}</option>"]
        for cl in course_level_values:
            sel = "selected" if cl == selected_course_level else ""
            cl_options.append(f"<option value='{cl}' {sel}>{cl}</option>")

        class_candidates = fetch_class_candidates(conn, query.get("form_class_q", ""), limit=10)
        if selected_schedule and not selected_form_class_id:
            selected_form_class_id = str(selected_schedule['class_id'])
        selected_form_class = conn.execute(
            """SELECT c.id, c.name, c.teacher_id, co.name AS course_name, l.name AS level_name, u.name AS teacher_name,
            (SELECT COUNT(*) FROM students s WHERE s.current_class_id=c.id) AS student_count
            FROM classes c
            LEFT JOIN courses co ON co.id=c.course_id
            LEFT JOIN levels l ON l.id=c.level_id
            LEFT JOIN users u ON u.id=c.teacher_id
            WHERE c.id=?""",
            (selected_form_class_id,),
        ).fetchone() if selected_form_class_id else None

        selected_schedule_day = selected_schedule['day_of_week'] if selected_schedule else ''
        selected_schedule_status = selected_schedule['status'] if selected_schedule else 'active'
        selected_teacher_form = str((selected_schedule['teacher_id'] if selected_schedule and selected_schedule['teacher_id'] else (selected_form_class['teacher_id'] if selected_form_class and selected_form_class['teacher_id'] else '')) or '')
        teacher_select_options = ["<option value=''>-</option>"]
        for tr in teacher_rows:
            sel = "selected" if str(tr['id']) == selected_teacher_form else ""
            teacher_select_options.append(f"<option value='{tr['id']}' {sel}>{tr['name']}</option>")

        selected_room_form = (selected_schedule['classroom'] if selected_schedule else '') or ''
        master_rooms = [r['name'] for r in conn.execute("SELECT name FROM classrooms ORDER BY name").fetchall()]
        existing_rooms = sorted(set(master_rooms) | {(r['classroom'] or '').strip() for r in schedules if (r['classroom'] or '').strip()} | ({selected_room_form} if selected_room_form else set()))
        room_options = [f"<option value=''>{t('academics.day_all')}</option>"]
        for r in existing_rooms:
            sel = "selected" if r == selected_room_form else ""
            room_options.append(f"<option value='{r}' {sel}>{r}</option>")
        day_select_options = [f"<option value=''>{t('academics.day_all')}</option>"]
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            sel = "selected" if selected_schedule_day == d else ""
            day_select_options.append(f"<option value='{d}' {sel}>{d}</option>")
        common_time_slots = ["16:25", "17:20", "17:25", "18:20", "18:30", "19:25", "19:35", "20:30"]
        start_time_options = [f"<option value=''>{t('academics.day_all')}</option>"]
        end_time_options = [f"<option value=''>{t('academics.day_all')}</option>"]
        selected_start = selected_schedule['start_time'] if selected_schedule else ''
        selected_end = selected_schedule['end_time'] if selected_schedule else ''
        for tm in common_time_slots:
            s_sel = "selected" if selected_start == tm else ""
            e_sel = "selected" if selected_end == tm else ""
            start_time_options.append(f"<option value='{tm}' {s_sel}>{tm}</option>")
            end_time_options.append(f"<option value='{tm}' {e_sel}>{tm}</option>")

        form_class_picker = render_picker_block(
            t("picker.class"),
            "form_class_q",
            query.get("form_class_q", ""),
            "selected_form_class_id",
            selected_form_class_id,
            (selected_form_class['name'] if selected_form_class else ""),
            class_candidates,
            "/academics",
            CURRENT_LANG,
            {
                "week": str(week_offset), "day": selected_day, "teacher_id": selected_teacher_id,
                "classroom": selected_room, "course_level": selected_course_level, "class_q": selected_class_q,
                "schedule_id": selected_schedule_id,
            }
        )

        detail_html = f"<div class='card'><h4>{t('academics.lesson_detail')}</h4><p class='empty-msg'>{t('common.no_data')}</p></div>"
        register_forms = f"<div class='card'><a class='btn secondary' href='/masterdata?lang={CURRENT_LANG}'>{t('academics.go_structure')}</a></div>"
        if selected_schedule:
            stu_rows = conn.execute("SELECT name_ko FROM students WHERE current_class_id=? ORDER BY id LIMIT 20", (selected_schedule['class_id'],)).fetchall()
            stu_text = ", ".join([r['name_ko'] for r in stu_rows]) if stu_rows else "-"
            detail_html = f"""
            <div class='card'>
              <h4>{t('academics.lesson_detail')}</h4>
              <table>
                <tr><th>{t('academics.class_name')}</th><td>{selected_schedule['class_name'] or '-'}</td></tr>
                <tr><th>{t('academics.course_level')}</th><td>{selected_schedule['course_name'] or '-'} / {selected_schedule['level_name'] or '-'}</td></tr>
                <tr><th>{t('academics.teacher')}</th><td>{selected_schedule['teacher_name'] or '-'}</td></tr>
                <tr><th>{t('academics.time_slot')}</th><td>{selected_schedule['day_of_week'] or '-'} {selected_schedule['start_time'] or '-'}~{selected_schedule['end_time'] or '-'}</td></tr>
                <tr><th>{t('academics.classroom')}</th><td>{selected_schedule['classroom'] or '-'}</td></tr>
                <tr><th>{t('academics.status')}</th><td><span class='badge {selected_schedule['status'] or ''}'>{status_t(selected_schedule['status']) if selected_schedule['status'] else '-'}</span></td></tr>
                <tr><th>{t('field.note')}</th><td>{selected_schedule['note'] or '-'}</td></tr>
                <tr><th>{t('students.field.name_ko')}</th><td>{stu_text}</td></tr>
              </table>
              <div class='lesson-actions' style='margin-top:10px'>
                <a class='btn' href='/classes/{selected_schedule['class_id']}?lang={CURRENT_LANG}'>{t('academics.view_class')}</a>
                <a class='btn' href='/attendance?lang={CURRENT_LANG}&selected_class_id={selected_schedule['class_id']}'>{t('academics.go_attendance')}</a>
                <a class='btn' href='/homework?lang={CURRENT_LANG}&selected_class_id={selected_schedule['class_id']}'>{t('academics.go_homework')}</a>
                <a class='btn' href='/exams?lang={CURRENT_LANG}&selected_class_id={selected_schedule['class_id']}'>{t('academics.go_exams')}</a>
              </div>
            </div>
            """

        html = render_html(t('academics.timetable_title'), f"""
        <div class='card'>
          <div class='muted'>{t('academics.timetable_desc')}</div>
        </div>
        <div class='card'>
          <h4>{t('academics.filter')}</h4>
          <form method='get' class='filter-row'>
            <input type='hidden' name='lang' value='{CURRENT_LANG}'>
            <input type='hidden' name='week' value='{week_offset}'>
            <label>{t('academics.week_current')} <strong>{week_label}</strong></label>
            <a class='btn secondary' href='/schedule?lang={CURRENT_LANG}&week={week_offset-1}'>{t('academics.week_prev')}</a>
            <a class='btn secondary' href='/schedule?lang={CURRENT_LANG}&week=0'>{t('academics.week_current')}</a>
            <a class='btn secondary' href='/schedule?lang={CURRENT_LANG}&week={week_offset+1}'>{t('academics.week_next')}</a>
            <label>{t('academics.day_filter')} <select name='day'>{''.join(day_options)}</select></label>
            <label>{t('academics.teacher_filter')} <select name='teacher_id'>{''.join(selected_teacher_options)}</select></label>
            <label>{t('academics.classroom_filter')} <input name='classroom' value='{selected_room}'></label>
            <label>{t('academics.course_level_filter')} <select name='course_level'>{''.join(cl_options)}</select></label>
            <label>{t('academics.class_filter')} <input name='class_q' value='{selected_class_q}'></label>
            <button>{t('academics.search')}</button>
            <a class='btn secondary' href='/schedule?lang={CURRENT_LANG}'>{t('common.reset')}</a>
            <a class='btn' href='#schedule-form'>{t('academics.add_lesson')}</a>
          </form>
        </div>

        <div class='two-col'>
          <div>
            <div class='card'>
              <h4>{t('academics.timetable')}</h4>
              <div class='timetable-wrap'>
                <div class='timetable-grid' style='grid-template-columns: 220px repeat({len(time_slots)}, minmax(180px,1fr));'>
                  {''.join(timetable_cols)}
                  {timetable_cells}
                </div>
              </div>
            </div>
            <div class='card' id='schedule-form'>
              <h4>{t('academics.schedule_form')}</h4>
              {form_class_picker}
              <form method='post' class='filter-row'>
                <input type='hidden' name='type' value='schedule'>
                <input type='hidden' name='schedule_id' value='{selected_schedule['id'] if selected_schedule else ''}'>
                <input type='hidden' name='selected_form_class_id' value='{selected_form_class_id}'>
                <label>{t('academics.schedule_pick_class')} <input value='{selected_form_class['name'] if selected_form_class else '-'}' readonly></label>
                <label>{t('academics.course')} <input value='{selected_form_class['course_name'] if selected_form_class else '-'}' readonly></label>
                <label>{t('academics.level')} <input value='{selected_form_class['level_name'] if selected_form_class else '-'}' readonly></label>
                <label>{t('academics.schedule_pick_teacher')} <select name='teacher_id'>{''.join(teacher_select_options)}</select></label>
                <label>{t('academics.schedule_pick_student')} <input value='{selected_form_class['student_count'] if selected_form_class else 0}' readonly></label>
                <label>{t('academics.day_of_week')} <select name='day_of_week'>{''.join(day_select_options)}</select></label>
                <label>{t('academics.start_time')} <select name='start_time'>{''.join(start_time_options)}</select></label>
                <label>{t('academics.end_time')} <select name='end_time'>{''.join(end_time_options)}</select></label>
                <label>{t('academics.classroom')} <select name='classroom'>{''.join(room_options)}</select></label>
                <label>{t('academics.status')} <select name='status'>
                  <option value='active' {'selected' if selected_schedule_status=='active' else ''}>{status_t('active')}</option>
                  <option value='makeup' {'selected' if selected_schedule_status=='makeup' else ''}>{status_t('makeup')}</option>
                  <option value='cancelled' {'selected' if selected_schedule_status=='cancelled' else ''}>{status_t('cancelled')}</option>
                </select></label>
                <label>{t('field.note')} <input name='note' value='{selected_schedule['note'] if selected_schedule else ''}'></label>
                <button>{t('common.save')}</button>
              </form>
              <div class='muted'>{t('academics.schedule_autofill')} · {t('academics.schedule_teacher_auto')}</div>
            </div>
          </div>
          <div>
            {detail_html}
            {register_forms}
            <div class='card'>
              <h4>{t('academics.class_list')}</h4>
              <table>
                <tr><th>{t('academics.class_name')}</th><th>{t('academics.course')}</th><th>{t('academics.level')}</th><th>{t('academics.teacher')}</th><th>{t('academics.student_count')}</th></tr>
                {class_rows}
              </table>
            </div>
            <div class='card'>
              <h4>{t('academics.course')}</h4>
              <table><tr><th>{t('field.id')}</th><th>{t('academics.course_name')}</th><th>{t('field.created_at')}</th></tr>{course_rows}</table>
            </div>
            <div class='card'>
              <h4>{t('academics.level')}</h4>
              <table><tr><th>{t('field.id')}</th><th>{t('academics.level_name')}</th><th>{t('academics.course')}</th><th>{t('field.created_at')}</th></tr>{level_rows}</table>
            </div>
          </div>
        </div>
        """, user, current_menu="schedule", flash_msg=flash_msg, flash_type=flash_type)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    # 출결
    if path == "/attendance":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        selected_student_id = query.get("selected_student_id", "")
        selected_class_id = query.get("selected_class_id", "")
        selected_teacher_id = query.get("selected_teacher_id", "")
        flash_msg = ""
        flash_type = "success"
        student_candidates = fetch_student_candidates(conn, query.get("student_q", ""), limit=10)
        class_candidates = fetch_class_candidates(conn, query.get("class_q", ""), limit=10)
        teacher_candidates = fetch_teacher_candidates(conn, query.get("teacher_q", ""), limit=10)
        selected_student = conn.execute("SELECT id, name_ko, student_no FROM students WHERE id=?", (selected_student_id,)).fetchone() if selected_student_id else None
        selected_class = conn.execute("SELECT id, name FROM classes WHERE id=?", (selected_class_id,)).fetchone() if selected_class_id else None
        selected_teacher = conn.execute("SELECT id, name, username FROM users WHERE id=? AND role='teacher'", (selected_teacher_id,)).fetchone() if selected_teacher_id else None

        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            class_id = d.get("class_id") or selected_class_id
            student_input_id = d.get("student_id") or selected_student_id
            student_row = conn.execute("SELECT user_id FROM students WHERE id=?", (student_input_id,)).fetchone() if str(student_input_id).isdigit() else None
            student_id = student_row["user_id"] if student_row else student_input_id
            errs = []
            if not ensure_exists(conn, "classes", class_id):
                add_error(errs, "class_id", "존재하지 않는 반입니다")
            if not ensure_exists(conn, "users", student_id, extra_where="role='student'"):
                add_error(errs, "student_id", "존재하지 않는 학생입니다")
            if (d.get("status") or "") not in ("present", "late", "absent", "makeup"):
                add_error(errs, "status", "허용되지 않는 상태값입니다")
            if not is_valid_date(d.get("lesson_date") or ""):
                add_error(errs, "lesson_date", "YYYY-MM-DD 형식이어야 합니다")
            if has_role(user, [ROLE_TEACHER]):
                class_ok = conn.execute("SELECT id FROM classes WHERE id=? AND teacher_id=?", (class_id, user["id"])).fetchone()
                if not class_ok:
                    conn.close()
                    status, headers, body = forbidden_html(user, t('forbidden.teacher_class_only'))
                    start_response(status, headers)
                    return [body]
            created_by = d.get("teacher_id") or selected_teacher_id or user["id"]
            if errs:
                flash_msg = format_errors(errs)
                flash_type = "error"
                log_event(conn, "ERROR", path, "출결 저장 검증 실패", "\n".join(errs), user["id"])
            else:
                conn.execute("INSERT INTO attendance(class_id, student_id, lesson_date, status, note, created_by, created_at) VALUES(?,?,?,?,?,?,?)",
                             (class_id, student_id, d.get("lesson_date"), d.get("status"), d.get("note"), created_by, now()))
                if d.get("status") == "absent":
                    conn.execute("INSERT INTO notifications(type, target_user_id, payload, created_at) VALUES(?,?,?,?)",
                                 ("absence", student_id, json.dumps({"student_id": student_id, "date": d.get("lesson_date")}, ensure_ascii=False), now()))
                conn.commit()
                flash_msg = "출결이 저장되었습니다"

        if has_role(user, [ROLE_TEACHER]):
            rows = conn.execute("SELECT a.* FROM attendance a JOIN classes c ON c.id=a.class_id WHERE c.teacher_id=? ORDER BY a.id DESC LIMIT 200", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_STUDENT]):
            rows = conn.execute("SELECT * FROM attendance WHERE student_id=? ORDER BY id DESC LIMIT 200", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_PARENT]):
            rows = conn.execute("""SELECT a.* FROM attendance a JOIN students s ON s.user_id=a.student_id WHERE s.guardian_name=? ORDER BY a.id DESC LIMIT 200""", (user["name"],)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM attendance ORDER BY id DESC LIMIT 200").fetchall()

        student_picker = render_picker_block(t("picker.student"), "student_q", query.get("student_q", ""), "selected_student_id", selected_student_id,
                                            (f"{selected_student['name_ko']} ({selected_student['student_no'] or '-'})" if selected_student else ""),
                                            student_candidates, "/attendance", CURRENT_LANG,
                                            {"selected_class_id": selected_class_id, "selected_teacher_id": selected_teacher_id, "class_q": query.get("class_q", ""), "teacher_q": query.get("teacher_q", "")})
        class_picker = render_picker_block(t("picker.class"), "class_q", query.get("class_q", ""), "selected_class_id", selected_class_id,
                                          (selected_class["name"] if selected_class else ""),
                                          class_candidates, "/attendance", CURRENT_LANG,
                                          {"selected_student_id": selected_student_id, "selected_teacher_id": selected_teacher_id, "student_q": query.get("student_q", ""), "teacher_q": query.get("teacher_q", "")})
        teacher_picker = render_picker_block(t("picker.teacher"), "teacher_q", query.get("teacher_q", ""), "selected_teacher_id", selected_teacher_id,
                                            (f"{selected_teacher['name']} ({selected_teacher['username']})" if selected_teacher else ""),
                                            teacher_candidates, "/attendance", CURRENT_LANG,
                                            {"selected_student_id": selected_student_id, "selected_class_id": selected_class_id, "student_q": query.get("student_q", ""), "class_q": query.get("class_q", "")})

        row_html = "".join([f"<tr><td>{r['id']}</td><td>{r['class_id']}</td><td>{r['student_id']}</td><td>{r['lesson_date']}</td><td>{r['status']}</td><td>{r['note'] or '-'}</td></tr>" for r in rows])
        html = render_html(t("attendance.title"), f"""
        {student_picker}
        {class_picker}
        {teacher_picker}
        <div class='card'>
          <h4>{t("attendance.input")}</h4>
          <form method='post' class='filter-row'>
            <input type='hidden' name='student_id' value='{selected_student_id}'>
            <input type='hidden' name='class_id' value='{selected_class_id}'>
            <input type='hidden' name='teacher_id' value='{selected_teacher_id}'>
            <label>{t('field.student_id')} <input value='{selected_student_id}' readonly></label>
            <label>{t('field.class_id')} <input value='{selected_class_id}' readonly></label>
            <label>{t('field.teacher_id')} <input value='{selected_teacher_id}' readonly></label>
            <label>{t('field.date')} <input name='lesson_date' placeholder='2026-03-06'></label>
            <label>{t('field.status')} <select name='status'><option value='present'>{attendance_status_t('present')}</option><option value='late'>{attendance_status_t('late')}</option><option value='absent'>{attendance_status_t('absent')}</option><option value='makeup'>{attendance_status_t('makeup')}</option></select></label>
            <label>{t('field.note')} <input name='note'></label>
            <button>{t("common.save")}</button>
          </form>
        </div>
        <div class='card'>
          <h4>{t("attendance.list")}</h4>
          <table>
            <tr><th>{t("field.id")}</th><th>{t("field.class_id")}</th><th>{t("field.student_id")}</th><th>{t("field.date")}</th><th>{t("field.status")}</th><th>{t("field.note")}</th></tr>
            {row_html or f"<tr><td colspan='6' class='empty-msg'>{t('common.no_data')}</td></tr>"}
          </table>
        </div>
        """, user, current_menu="attendance", flash_msg=flash_msg, flash_type=flash_type)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path == "/homework":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        selected_class_id = query.get("selected_class_id", "")
        selected_teacher_id = query.get("selected_teacher_id", "")
        class_candidates = fetch_class_candidates(conn, query.get("class_q", ""), limit=10)
        teacher_candidates = fetch_teacher_candidates(conn, query.get("teacher_q", ""), limit=10)
        selected_class = conn.execute("SELECT id, name FROM classes WHERE id=?", (selected_class_id,)).fetchone() if selected_class_id else None
        selected_teacher = conn.execute("SELECT id, name, username FROM users WHERE id=? AND role='teacher'", (selected_teacher_id,)).fetchone() if selected_teacher_id else None

        if method == "POST":
            d = parse_body(environ)
            typ = d.get("type")
            if typ == "homework" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
                class_id = d.get("class_id") or selected_class_id
                if has_role(user, [ROLE_TEACHER]):
                    class_ok = conn.execute("SELECT id FROM classes WHERE id=? AND teacher_id=?", (class_id, user["id"])).fetchone()
                    if not class_ok:
                        conn.close()
                        status, headers, body = forbidden_html(user, t('forbidden.teacher_class_only'))
                        start_response(status, headers)
                        return [body]
                created_by = d.get("teacher_id") or selected_teacher_id or user["id"]
                conn.execute("INSERT INTO homework(class_id, title, due_date, created_by, created_at) VALUES(?,?,?,?,?)", (class_id, d.get("title"), d.get("due_date"), created_by, now()))
                conn.execute("INSERT INTO notifications(type, target_user_id, payload, created_at) VALUES(?,?,?,?)", ("homework", None, json.dumps({"title": d.get("title")}, ensure_ascii=False), now()))
            elif typ == "submission" and has_role(user, [ROLE_STUDENT]):
                conn.execute("INSERT INTO homework_submissions(homework_id, student_id, submitted, submitted_at) VALUES(?,?,?,?)", (d.get("homework_id"), user["id"], 1 if d.get("submitted") else 0, now()))
            elif typ == "feedback" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
                conn.execute("UPDATE homework_submissions SET feedback=?, feedback_by=?, feedback_at=? WHERE id=?", (d.get("feedback"), user["id"], now(), d.get("submission_id")))
            conn.commit()

        if has_role(user, [ROLE_TEACHER]):
            hw = conn.execute("SELECT h.* FROM homework h JOIN classes c ON c.id=h.class_id WHERE c.teacher_id=? ORDER BY h.id DESC", (user["id"],)).fetchall()
            sub = conn.execute("SELECT hs.* FROM homework_submissions hs JOIN homework h ON h.id=hs.homework_id JOIN classes c ON c.id=h.class_id WHERE c.teacher_id=? ORDER BY hs.id DESC", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_STUDENT]):
            hw = conn.execute("SELECT * FROM homework ORDER BY id DESC").fetchall()
            sub = conn.execute("SELECT * FROM homework_submissions WHERE student_id=? ORDER BY id DESC", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_PARENT]):
            hw = conn.execute("SELECT DISTINCT h.* FROM homework h JOIN homework_submissions hs ON hs.homework_id=h.id JOIN students s ON s.user_id=hs.student_id WHERE s.guardian_name=? ORDER BY h.id DESC", (user["name"],)).fetchall()
            sub = conn.execute("""SELECT hs.* FROM homework_submissions hs JOIN students s ON s.user_id=hs.student_id WHERE s.guardian_name=? ORDER BY hs.id DESC""", (user["name"],)).fetchall()
        else:
            hw = conn.execute("SELECT * FROM homework ORDER BY id DESC").fetchall()
            sub = conn.execute("SELECT * FROM homework_submissions ORDER BY id DESC").fetchall()

        class_picker = render_picker_block(t("picker.class"), "class_q", query.get("class_q", ""), "selected_class_id", selected_class_id,
                                          (selected_class["name"] if selected_class else ""), class_candidates, "/homework", CURRENT_LANG,
                                          {"selected_teacher_id": selected_teacher_id, "teacher_q": query.get("teacher_q", "")})
        teacher_picker = render_picker_block(t("picker.teacher"), "teacher_q", query.get("teacher_q", ""), "selected_teacher_id", selected_teacher_id,
                                            (f"{selected_teacher['name']} ({selected_teacher['username']})" if selected_teacher else ""), teacher_candidates, "/homework", CURRENT_LANG,
                                            {"selected_class_id": selected_class_id, "class_q": query.get("class_q", "")})
        hw_rows = "".join([f"<tr><td>{r['id']}</td><td>{r['class_id']}</td><td>{r['title']}</td><td>{r['due_date'] or '-'}</td><td>{r['created_by']}</td></tr>" for r in hw])
        sub_rows = "".join([f"<tr><td>{r['id']}</td><td>{r['homework_id']}</td><td>{r['student_id']}</td><td>{'Y' if r['submitted'] else '-'}</td><td>{r['feedback'] or '-'}</td></tr>" for r in sub])

        html = render_html(t("homework.title"), f"""
        {class_picker}
        {teacher_picker}
        <div class='card'>
          <h4>{t("homework.add")}</h4>
          <form method='post' class='filter-row'>
            <input type='hidden' name='type' value='homework'>
            <input type='hidden' name='class_id' value='{selected_class_id}'>
            <input type='hidden' name='teacher_id' value='{selected_teacher_id}'>
            <label>{t('field.class_id')} <input value='{selected_class_id}' readonly></label>
            <label>{t('field.teacher_id')} <input value='{selected_teacher_id}' readonly></label>
            <label>{t('field.title')} <input name='title'></label>
            <label>{t("field.due_date")} <input name='due_date' placeholder='2026-03-15'></label>
            <button>{t('common.save')}</button>
          </form>
        </div>
        <div class='card'>
          <h4>{t("homework.input")}</h4>
          <form method='post' class='filter-row'><input type='hidden' name='type' value='submission'>{t("field.homework_id")}<input name='homework_id'> {t('field.submitted')}<input type='checkbox' name='submitted' value='1'><button>{t('common.save')}</button></form>
          <form method='post' class='filter-row'><input type='hidden' name='type' value='feedback'>{t("field.submission_id")}<input name='submission_id'> {t("field.feedback")}<input name='feedback'><button>{t('common.save')}</button></form>
        </div>
        <div class='card'><h4>{t("homework.list")}</h4><table><tr><th>{t("field.id")}</th><th>{t("field.class_id")}</th><th>{t("field.title")}</th><th>{t("field.due_date")}</th><th>{t("field.writer")}</th></tr>{hw_rows or f"<tr><td colspan='5' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        <div class='card'><h4>{t("homework.submissions")}</h4><table><tr><th>{t("field.id")}</th><th>{t("field.homework_id")}</th><th>{t("field.student_id")}</th><th>{t("common.selected")}</th><th>{t("field.feedback")}</th></tr>{sub_rows or f"<tr><td colspan='5' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        """, user, current_menu="homework")
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path == "/exams":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        flash_msg = ""
        flash_type = "success"
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            typ = d.get("type")
            errs = []
            if has_role(user, [ROLE_TEACHER]):
                if typ == "exam":
                    class_ok = conn.execute("SELECT id FROM classes WHERE id=? AND teacher_id=?", (d.get("class_id"), user["id"])).fetchone()
                    if not class_ok:
                        conn.close()
                        status, headers, body = forbidden_html(user, t('forbidden.teacher_class_only'))
                        start_response(status, headers)
                        return [body]
                elif typ == "score":
                    exam_ok = conn.execute("""SELECT e.id FROM exams e JOIN classes c ON c.id=e.class_id WHERE e.id=? AND c.teacher_id=?""", (d.get("exam_id"), user["id"])).fetchone()
                    if not exam_ok:
                        conn.close()
                        status, headers, body = forbidden_html(user, t('forbidden.teacher_exam_only'))
                        start_response(status, headers)
                        return [body]
            if typ == "exam":
                if not ensure_exists(conn, "classes", d.get("class_id")):
                    add_error(errs, "class_id", "존재하지 않는 반입니다")
                if not (d.get("name") or "").strip():
                    add_error(errs, "name", "필수값입니다")
                if d.get("exam_date") and not is_valid_date(d.get("exam_date")):
                    add_error(errs, "exam_date", "YYYY-MM-DD 형식이어야 합니다")
                if d.get("linked_book_id") and not ensure_exists(conn, "books", d.get("linked_book_id")):
                    add_error(errs, "linked_book_id", "존재하지 않는 도서입니다")
                if not errs:
                    conn.execute("INSERT INTO exams(class_id, name, exam_date, report, linked_book_id, created_at) VALUES(?,?,?,?,?,?)", (d.get("class_id"), d.get("name"), d.get("exam_date"), d.get("report"), d.get("linked_book_id") or None, now()))
            elif typ == "score":
                score_v = as_float(d.get("score"))
                if not ensure_exists(conn, "exams", d.get("exam_id")):
                    add_error(errs, "exam_id", "존재하지 않는 시험입니다")
                if not ensure_exists(conn, "users", d.get("student_id"), extra_where="role='student'"):
                    add_error(errs, "student_id", "존재하지 않는 학생입니다")
                if score_v is None or score_v < 0 or score_v > 100:
                    add_error(errs, "score", "0~100 범위의 숫자여야 합니다")
                if not errs:
                    conn.execute("INSERT INTO exam_scores(exam_id, student_id, score, created_at) VALUES(?,?,?,?)", (d.get("exam_id"), d.get("student_id"), score_v, now()))
            if errs:
                flash_msg = format_errors(errs)
                flash_type = "error"
                log_event(conn, "ERROR", path, "시험/성적 저장 검증 실패", "\n".join(errs), user["id"])
            else:
                conn.commit()
                flash_msg = "저장되었습니다"
        if has_role(user, [ROLE_TEACHER]):
            exams = conn.execute("SELECT e.* FROM exams e JOIN classes c ON c.id=e.class_id WHERE c.teacher_id=? ORDER BY e.id DESC", (user["id"],)).fetchall()
            scores = conn.execute("SELECT es.* FROM exam_scores es JOIN exams e ON e.id=es.exam_id JOIN classes c ON c.id=e.class_id WHERE c.teacher_id=? ORDER BY es.id DESC", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_STUDENT]):
            exams = conn.execute("SELECT e.* FROM exams e JOIN exam_scores es ON es.exam_id=e.id WHERE es.student_id=? ORDER BY e.id DESC", (user["id"],)).fetchall()
            scores = conn.execute("SELECT * FROM exam_scores WHERE student_id=? ORDER BY id DESC", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_PARENT]):
            exams = conn.execute("SELECT DISTINCT e.* FROM exams e JOIN exam_scores es ON es.exam_id=e.id JOIN students s ON s.user_id=es.student_id WHERE s.guardian_name=? ORDER BY e.id DESC", (user["name"],)).fetchall()
            scores = conn.execute("SELECT es.* FROM exam_scores es JOIN students s ON s.user_id=es.student_id WHERE s.guardian_name=? ORDER BY es.id DESC", (user["name"],)).fetchall()
        else:
            exams = conn.execute("SELECT * FROM exams ORDER BY id DESC").fetchall()
            scores = conn.execute("SELECT * FROM exam_scores ORDER BY id DESC").fetchall()

        exam_rows = "".join([f"<tr><td>{r['id']}</td><td>{r['class_id']}</td><td>{r['name']}</td><td>{r['exam_date'] or '-'}</td><td>{r['report'] or '-'}</td></tr>" for r in exams])
        score_rows = "".join([f"<tr><td>{r['id']}</td><td>{r['exam_id']}</td><td>{r['student_id']}</td><td>{r['score']}</td></tr>" for r in scores])
        html = render_html(t("exams.title"), f"""
        <div class='card'><h4>{t("exams.add")}</h4><form method='post' class='filter-row'><input type='hidden' name='type' value='exam'>{t("field.class_id")}<input name='class_id'> {t("field.exam_name")}<input name='name'> {t("field.exam_date")}<input name='exam_date'> {t("field.report")}<input name='report'> {t("field.book_id")}<input name='linked_book_id'><button>{t('common.save')}</button></form></div>
        <div class='card'><h4>{t("exams.score_input")}</h4><form method='post' class='filter-row'><input type='hidden' name='type' value='score'>{t("field.exam_id")}<input name='exam_id'> {t("field.student_id")}<input name='student_id'> {t("field.score")}<input name='score'><button>{t('common.save')}</button></form></div>
        <div class='card'><h4>{t("exams.list")}</h4><table><tr><th>{t("field.id")}</th><th>{t("field.class_id")}</th><th>{t("field.exam_name")}</th><th>{t("field.exam_date")}</th><th>{t("field.report")}</th></tr>{exam_rows or f"<tr><td colspan='5' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        <div class='card'><h4>{t("exams.scores")}</h4><table><tr><th>{t("field.id")}</th><th>{t("field.exam_id")}</th><th>{t("field.student_id")}</th><th>{t("field.score")}</th></tr>{score_rows or f"<tr><td colspan='4' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        """, user, current_menu="exams", flash_msg=flash_msg, flash_type=flash_type)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path == "/counseling":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        flash_msg = ""
        flash_type = "success"
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            errs = []
            if not ensure_exists(conn, "users", d.get("student_id"), extra_where="role='student'"):
                add_error(errs, "student_id", "존재하지 않는 학생입니다")
            if d.get("parent_id") and not ensure_exists(conn, "users", d.get("parent_id"), extra_where="role='parent'"):
                add_error(errs, "parent_id", "존재하지 않는 학부모입니다")
            if not (d.get("memo") or "").strip():
                add_error(errs, "memo", "필수값입니다")
            if errs:
                flash_msg = format_errors(errs)
                flash_type = "error"
                log_event(conn, "ERROR", path, "상담 저장 검증 실패", "\n".join(errs), user["id"])
            else:
                conn.execute("INSERT INTO counseling(student_id, parent_id, memo, is_special_note, created_by, created_at) VALUES(?,?,?,?,?,?)", (d.get("student_id"), d.get("parent_id") or None, d.get("memo"), 1 if d.get("is_special_note") else 0, user["id"], now()))
                conn.commit()
                flash_msg = "저장되었습니다"
        rows = conn.execute("SELECT * FROM counseling ORDER BY id DESC").fetchall()
        table_rows = "".join([
            f"<tr><td>{r['id']}</td><td>{r['student_id']}</td><td>{r['parent_id'] or '-'}</td><td>{r['memo'] or '-'}</td><td>{'Y' if r['is_special_note'] else '-'}</td><td>{r['created_at'] or '-'}</td></tr>"
            for r in rows
        ])
        html = render_html(t("counseling.title"), f"""
        <div class='card'>
          <form method='post' class='filter-row'>
            <label>{t('counseling.student_id')} <input name='student_id'></label>
            <label>{t('counseling.parent_id')} <input name='parent_id'></label>
            <label>{t('counseling.memo')} <input name='memo'></label>
            <label>{t('counseling.special')} <input type='checkbox' name='is_special_note' value='1'></label>
            <button>{t("common.save")}</button>
          </form>
        </div>
        <div class='card'>
          <h4>{t('counseling.list')}</h4>
          <table>
            <tr><th>ID</th><th>{t('counseling.student_id')}</th><th>{t('counseling.parent_id')}</th><th>{t('counseling.memo')}</th><th>{t('counseling.special')}</th><th>created_at</th></tr>
            {table_rows or f"<tr><td colspan='6' class='empty-msg'>{t('common.no_data')}</td></tr>"}
          </table>
        </div>
        """, user, current_menu="counseling", flash_msg=flash_msg, flash_type=flash_type)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path == "/payments":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_PARENT, ROLE_STUDENT]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        selected_student_id = query.get("selected_student_id", "")
        student_candidates = fetch_student_candidates(conn, query.get("student_q", ""), limit=10)
        selected_student = conn.execute("SELECT id, name_ko, student_no FROM students WHERE id=?", (selected_student_id,)).fetchone() if selected_student_id else None
        flash_msg = ""
        flash_type = "success"
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            d = parse_body(environ)
            student_input_id = d.get("student_id") or selected_student_id
            student_row = conn.execute("SELECT user_id FROM students WHERE id=?", (student_input_id,)).fetchone() if str(student_input_id).isdigit() else None
            student_user_id = student_row["user_id"] if student_row else student_input_id
            errs = []
            amount_v = as_float(d.get("amount"))
            hours_v = as_float(d.get("package_hours") or 0)
            remain_v = as_int(d.get("remaining_classes") or 0)
            if not ensure_exists(conn, "users", student_user_id, extra_where="role='student'"):
                add_error(errs, "student_id", "존재하지 않는 학생입니다")
            if not is_valid_date(d.get("paid_date") or ""):
                add_error(errs, "paid_date", "YYYY-MM-DD 형식이어야 합니다")
            if amount_v is None or amount_v < 0:
                add_error(errs, "amount", "0 이상의 숫자여야 합니다")
            if hours_v is None or hours_v < 0:
                add_error(errs, "package_hours", "0 이상의 숫자여야 합니다")
            if remain_v is None or remain_v < 0:
                add_error(errs, "remaining_classes", "0 이상의 정수여야 합니다")
            if errs:
                flash_msg = format_errors(errs)
                flash_type = "error"
                log_event(conn, "ERROR", path, "수납 저장 검증 실패", "\n".join(errs), user["id"])
            else:
                conn.execute("INSERT INTO payments(student_id, paid_date, amount, package_hours, remaining_classes, created_at) VALUES(?,?,?,?,?,?)", (student_user_id, d.get("paid_date"), amount_v, hours_v, remain_v, now()))
                conn.commit()
                flash_msg = "저장되었습니다"
        if has_role(user, [ROLE_STUDENT]):
            rows = conn.execute("SELECT * FROM payments WHERE student_id=? ORDER BY id DESC", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_PARENT]):
            rows = conn.execute("SELECT p.* FROM payments p JOIN students s ON s.user_id=p.student_id WHERE s.guardian_name=? ORDER BY p.id DESC", (user["name"],)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM payments ORDER BY id DESC").fetchall()

        student_picker = render_picker_block(t("picker.student"), "student_q", query.get("student_q", ""), "selected_student_id", selected_student_id,
                                            (f"{selected_student['name_ko']} ({selected_student['student_no'] or '-'})" if selected_student else ""),
                                            student_candidates, "/payments", CURRENT_LANG, {})
        row_html = "".join([f"<tr><td>{r['id']}</td><td>{r['student_id']}</td><td>{r['paid_date']}</td><td>{r['amount']}</td><td>{r['package_hours']}</td><td>{r['remaining_classes']}</td></tr>" for r in rows])
        html = render_html(t("payments.title"), f"""
        {student_picker if has_role(user, [ROLE_OWNER, ROLE_MANAGER]) else ''}
        <div class='card'>
          <h4>{t("payments.input")}</h4>
          <form method='post' class='filter-row'>
            <input type='hidden' name='student_id' value='{selected_student_id}'>
            <label>{t('field.student_id')} <input value='{selected_student_id}' readonly></label>
            <label>{t("field.paid_date")} <input name='paid_date' placeholder='2026-03-06'></label>
            <label>{t("field.amount")} <input name='amount'></label>
            <label>{t("field.package_hours")} <input name='package_hours'></label>
            <label>{t("field.remaining_classes")} <input name='remaining_classes'></label>
            <button>{t('common.save')}</button>
          </form>
        </div>
        <div class='card'><h4>{t("payments.list")}</h4><table><tr><th>{t("field.id")}</th><th>{t("field.student_id")}</th><th>{t("field.paid_date")}</th><th>{t("field.amount")}</th><th>{t("field.package_hours")}</th><th>{t("field.remaining_classes")}</th></tr>{row_html or f"<tr><td colspan='6' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        """, user, current_menu="payments", flash_msg=flash_msg, flash_type=flash_type)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path == "/announcements":
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            conn.execute("INSERT INTO announcements(title, content, created_by, created_at) VALUES(?,?,?,?)", (d.get("title"), d.get("content"), user["id"], now()))
            conn.commit()
        rows = conn.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
        noti = conn.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50").fetchall()
        ann_rows = "".join([f"<tr><td>{r['id']}</td><td>{r['title']}</td><td>{r['content']}</td><td>{r['created_by']}</td><td>{r['created_at']}</td></tr>" for r in rows])
        noti_rows = "".join([f"<tr><td>{r['id']}</td><td>{r['type']}</td><td>{r['target_user_id'] or '-'}</td><td>{r['payload']}</td><td>{r['created_at']}</td></tr>" for r in noti])
        html = render_html(t("ann.title"), f"""
        <div class='card'><h4>{t("ann.write")}</h4><form method='post' class='filter-row'>{t("field.title")}<input name='title'> {t('field.content')}<input name='content'><button>{t('common.save')}</button></form></div>
        <div class='card'><h4>{t("ann.list")}</h4><table><tr><th>{t("field.id")}</th><th>{t("field.title")}</th><th>{t("field.content")}</th><th>{t("field.writer")}</th><th>{t("field.created_at")}</th></tr>{ann_rows or f"<tr><td colspan='5' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        <div class='card'><h4>{t("ann.noti")}</h4><table><tr><th>{t("field.id")}</th><th>{t("field.type")}</th><th>{t("field.target")}</th><th>{t("field.data")}</th><th>{t("field.created_at")}</th></tr>{noti_rows or f"<tr><td colspan='5' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        """, user, current_menu="announcements")
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path == "/library":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        selected_student_id = query.get("selected_student_id", "")
        selected_teacher_id = query.get("selected_teacher_id", "")
        student_candidates = fetch_student_candidates(conn, query.get("student_q", ""), limit=10)
        teacher_candidates = fetch_teacher_candidates(conn, query.get("teacher_q", ""), limit=10)
        selected_student = conn.execute("SELECT id, name_ko, student_no FROM students WHERE id=?", (selected_student_id,)).fetchone() if selected_student_id else None
        selected_teacher = conn.execute("SELECT id, name, username FROM users WHERE id=? AND role='teacher'", (selected_teacher_id,)).fetchone() if selected_teacher_id else None
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            typ = d.get("type")
            if typ == "book":
                conn.execute("INSERT INTO books(code, title, status, created_at) VALUES(?,?,?,?)", (d.get("code"), d.get("title"), "available", now()))
            elif typ == "loan":
                book = conn.execute("SELECT * FROM books WHERE code=?", (d.get("code"),)).fetchone()
                if book:
                    conn.execute("UPDATE books SET status='borrowed' WHERE id=?", (book["id"],))
                    student_input_id = d.get("student_id") or selected_student_id
                    student_row = conn.execute("SELECT user_id FROM students WHERE id=?", (student_input_id,)).fetchone() if str(student_input_id).isdigit() else None
                    student_user_id = student_row["user_id"] if student_row else student_input_id
                    conn.execute("INSERT INTO book_loans(book_id, student_id, loaned_at, handled_by, created_at) VALUES(?,?,?,?,?)", (book["id"], student_user_id, now(), d.get("teacher_id") or selected_teacher_id or user["id"], now()))
            elif typ == "return":
                book = conn.execute("SELECT * FROM books WHERE code=?", (d.get("code"),)).fetchone()
                if book:
                    conn.execute("UPDATE books SET status='available' WHERE id=?", (book["id"],))
                    conn.execute("UPDATE book_loans SET returned_at=? WHERE book_id=? AND returned_at IS NULL", (now(), book["id"]))
            conn.commit()
        books = conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
        loans = conn.execute("SELECT * FROM book_loans ORDER BY id DESC").fetchall()
        student_picker = render_picker_block(t("picker.student"), "student_q", query.get("student_q", ""), "selected_student_id", selected_student_id,
                                            (f"{selected_student['name_ko']} ({selected_student['student_no'] or '-'})" if selected_student else ""),
                                            student_candidates, "/library", CURRENT_LANG,
                                            {"selected_teacher_id": selected_teacher_id, "teacher_q": query.get("teacher_q", "")})
        teacher_picker = render_picker_block(t("picker.teacher"), "teacher_q", query.get("teacher_q", ""), "selected_teacher_id", selected_teacher_id,
                                            (f"{selected_teacher['name']} ({selected_teacher['username']})" if selected_teacher else ""),
                                            teacher_candidates, "/library", CURRENT_LANG,
                                            {"selected_student_id": selected_student_id, "student_q": query.get("student_q", "")})
        book_rows = "".join([f"<tr><td>{r['id']}</td><td>{r['code']}</td><td>{r['title']}</td><td>{r['status']}</td></tr>" for r in books])
        loan_rows = "".join([f"<tr><td>{r['id']}</td><td>{r['book_id']}</td><td>{r['student_id']}</td><td>{r['loaned_at']}</td><td>{r['returned_at'] or '-'}</td><td>{r['handled_by']}</td></tr>" for r in loans])
        html = render_html(t("library.title"), f"""
        {student_picker}
        {teacher_picker}
        <div class='card'><h4>{t("library.book_add")}</h4><form method='post' class='filter-row'><input type='hidden' name='type' value='book'>{t("field.code")}<input name='code'> {t("field.title")}<input name='title'><button>{t('common.save')}</button></form></div>
        <div class='card'><h4>{t("library.loan")}</h4><form method='post' class='filter-row'><input type='hidden' name='type' value='loan'><input type='hidden' name='student_id' value='{selected_student_id}'><input type='hidden' name='teacher_id' value='{selected_teacher_id}'>{t("field.code")}<input name='code'> {t("field.student_id")}<input value='{selected_student_id}' readonly> {t("field.teacher_id")}<input value='{selected_teacher_id}' readonly><button>{t('common.save')}</button></form></div>
        <div class='card'><h4>{t("library.return")}</h4><form method='post' class='filter-row'><input type='hidden' name='type' value='return'>{t("field.code")}<input name='code'><button>{t('common.save')}</button></form></div>
        <div class='card'><h4>{t("library.books")}</h4><table><tr><th>{t("field.id")}</th><th>{t("field.code")}</th><th>{t("field.title")}</th><th>{t("field.status")}</th></tr>{book_rows or f"<tr><td colspan='4' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        <div class='card'><h4>{t("library.history")}</h4><table><tr><th>{t("field.id")}</th><th>{t("field.book_id")}</th><th>{t("field.student_id")}</th><th>{t("field.loaned_at")}</th><th>{t("field.returned_at")}</th><th>{t("field.handler")}</th></tr>{loan_rows or f"<tr><td colspan='6' class='empty-msg'>{t('common.no_data')}</td></tr>"}</table></div>
        """, user, current_menu="library")
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path == "/logs":
        if not has_role(user, [ROLE_OWNER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        rows = conn.execute("SELECT id, level, route, user_id, message, detail, created_at FROM app_logs ORDER BY id DESC LIMIT 300").fetchall()
        row_html = "".join([
            f"<tr><td>{r['id']}</td><td>{r['level']}</td><td>{r['route'] or '-'}</td><td>{r['user_id'] or '-'}</td><td>{r['message']}</td><td>{(r['detail'] or '-')}</td><td>{r['created_at']}</td></tr>"
            for r in rows
        ])
        html = render_html(menu_t("logs"), f"""
        <div class='card'>
          <h4>{menu_t('logs')}</h4>
          <table>
            <tr><th>ID</th><th>level</th><th>route</th><th>user_id</th><th>message</th><th>detail</th><th>created_at</th></tr>
            {row_html or f"<tr><td colspan='7' class='empty-msg'>{t('common.no_data')}</td></tr>"}
          </table>
        </div>
        """, user, current_menu="logs")
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]
    if path == "/api/announcements" and method == "GET":
        rows = conn.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
        conn.close()
        status, headers, body = json_resp([dict(r) for r in rows])
        start_response(status, headers)
        return [body]
    if path == "/api/books/loan-by-code" and method == "POST":
        d = parse_body(environ)
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            conn.close()
            status, headers, body = forbidden_json()
            start_response(status, headers)
            return [body]
        book = conn.execute("SELECT * FROM books WHERE code=?", (d.get("code"),)).fetchone()
        if not book:
            conn.close()
            status, headers, body = json_resp({"error": t('library.not_found')}, "404 Not Found")
            start_response(status, headers)
            return [body]
        conn.execute("UPDATE books SET status='borrowed' WHERE id=?", (book["id"],))
        student_input_id = d.get("student_id")
        student_row = conn.execute("SELECT user_id FROM students WHERE id=?", (student_input_id,)).fetchone() if str(student_input_id).isdigit() else None
        student_user_id = student_row["user_id"] if student_row else student_input_id
        conn.execute("INSERT INTO book_loans(book_id, student_id, loaned_at, handled_by, created_at) VALUES(?,?,?,?,?)", (book["id"], student_user_id, now(), user["id"], now()))
        conn.commit()
        conn.close()
        status, headers, body = json_resp({"message": t('library.loan_done')})
        start_response(status, headers)
        return [body]
    conn.close()
    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
    return ["Not Found".encode("utf-8")]
if __name__ == "__main__":
    init_db()
    with make_server("0.0.0.0", 8000, app) as httpd:
        print(t('server.start') + ': http://127.0.0.1:8000')
        httpd.serve_forever()
