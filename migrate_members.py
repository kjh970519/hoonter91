#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
그누보드4 회원 데이터를 Zigger로 마이그레이션하는 스크립트
"""
import subprocess
import re

# 게시판 목록
BOARDS = [
    "story_album", "story_basketball", "story_boxing", "story_family",
    "story_julye", "story_sports_video", "bucheon_college", "military_academy",
    "youth_sports", "lecture_career", "jinyong_free", "community_notice",
    "community_free", "community_pds", "community_qna"
]

def run_mysql_local(query):
    """로컬 MySQL (백업 DB) 쿼리 실행"""
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "root", "-p1234",
           "--default-character-set=utf8", "hoonter91_backup", "-N", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Local MySQL Error:", result.stderr)
    return result.stdout.strip()

def run_mysql_remote(query):
    """원격 MySQL (운영 DB) 쿼리 실행"""
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "hoonter91", "-phoon45789",
           "-h", "49.50.129.138", "--default-character-set=utf8", "hoonter91", "-N", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Remote MySQL Error:", result.stderr)
    return result.stdout.strip()

def run_mysql_remote_update(query):
    """원격 MySQL UPDATE 실행"""
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "hoonter91", "-phoon45789",
           "-h", "49.50.129.138", "--default-character-set=utf8", "hoonter91", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Remote MySQL Error:", result.stderr)
        return False
    return True

def escape_sql(s):
    if s is None:
        return ""
    s = str(s)
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace('"', '\\"')
    return s

def get_g4_members():
    """그누보드4 회원 목록 조회"""
    query = """
    SELECT mb_no, mb_id, mb_password, mb_name, mb_nick, mb_email,
           mb_level, mb_sex, mb_hp, mb_tel,
           CONCAT(mb_addr1, ' ', mb_addr2) as address,
           mb_today_login, mb_login_ip, mb_point, mb_datetime,
           mb_leave_date, mb_1, mb_2, mb_3, mb_4, mb_5, mb_6, mb_7, mb_8, mb_9, mb_10
    FROM g4_member
    ORDER BY mb_no
    """
    result = run_mysql_local(query)

    members = []
    if result:
        for line in result.split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 15:
                members.append({
                    'mb_no': parts[0],
                    'mb_id': parts[1],
                    'mb_password': parts[2],
                    'mb_name': parts[3],
                    'mb_nick': parts[4],
                    'mb_email': parts[5],
                    'mb_level': parts[6],
                    'mb_sex': parts[7],
                    'mb_hp': parts[8] if len(parts) > 8 else '',
                    'mb_tel': parts[9] if len(parts) > 9 else '',
                    'mb_address': parts[10] if len(parts) > 10 else '',
                    'mb_today_login': parts[11] if len(parts) > 11 else None,
                    'mb_login_ip': parts[12] if len(parts) > 12 else '',
                    'mb_point': parts[13] if len(parts) > 13 else '0',
                    'mb_datetime': parts[14] if len(parts) > 14 else None,
                    'mb_leave_date': parts[15] if len(parts) > 15 else '',
                    'mb_1': parts[16] if len(parts) > 16 else '',
                    'mb_2': parts[17] if len(parts) > 17 else '',
                    'mb_3': parts[18] if len(parts) > 18 else '',
                    'mb_4': parts[19] if len(parts) > 19 else '',
                    'mb_5': parts[20] if len(parts) > 20 else '',
                    'mb_6': parts[21] if len(parts) > 21 else '',
                    'mb_7': parts[22] if len(parts) > 22 else '',
                    'mb_8': parts[23] if len(parts) > 23 else '',
                    'mb_9': parts[24] if len(parts) > 24 else '',
                    'mb_10': parts[25] if len(parts) > 25 else '',
                })
    return members

def check_existing_member(mb_id):
    """기존 회원 존재 여부 확인"""
    query = f"SELECT mb_idx FROM zg_member WHERE mb_id = '{escape_sql(mb_id)}'"
    result = run_mysql_remote(query)
    return result.strip() if result else None

def insert_member(member, dry_run=True):
    """회원 데이터 삽입"""
    # 성별 변환 (M/F)
    gender = 'M'
    if member['mb_sex'] == 'F':
        gender = 'F'

    # 레벨 변환 (그누보드: 높을수록 관리자 / Zigger: 1이 최고관리자)
    # 그누보드: 10=최고관리자, 1=일반회원
    # Zigger: 1=최고관리자, 9=일반회원
    level = 9  # 기본값
    g4_level = int(member['mb_level']) if member['mb_level'] else 2
    if g4_level >= 10:
        level = 1  # 최고관리자
    elif g4_level >= 5:
        level = 5  # 중간관리자
    elif g4_level >= 3:
        level = 7  # 스태프
    else:
        level = 9  # 일반회원

    # 탈퇴일 처리
    dregdate = 'NULL'
    if member['mb_leave_date'] and member['mb_leave_date'] != '':
        dregdate = f"'{member['mb_leave_date']}'"

    # 최근 로그인
    lately = 'NULL'
    if member['mb_today_login'] and member['mb_today_login'] != '0000-00-00 00:00:00':
        lately = f"'{member['mb_today_login']}'"

    # 가입일
    regdate = 'NULL'
    if member['mb_datetime'] and member['mb_datetime'] != '0000-00-00 00:00:00':
        regdate = f"'{member['mb_datetime']}'"

    query = f"""
    INSERT INTO zg_member
    (mb_id, mb_email, mb_pwd, mb_name, mb_level, mb_gender, mb_phone, mb_telephone,
     mb_address, mb_lately, mb_lately_ip, mb_point, mb_regdate, mb_dregdate,
     mb_1, mb_2, mb_3, mb_4, mb_5, mb_6, mb_7, mb_8, mb_9, mb_10, mb_adm, mb_exp)
    VALUES
    ('{escape_sql(member['mb_id'])}', '{escape_sql(member['mb_email'])}',
     '{escape_sql(member['mb_password'])}', '{escape_sql(member['mb_name'])}',
     {level}, '{gender}', '{escape_sql(member['mb_hp'])}', '{escape_sql(member['mb_tel'])}',
     '{escape_sql(member['mb_address'])}', {lately}, '{escape_sql(member['mb_login_ip'])}',
     {member['mb_point'] or 0}, {regdate}, {dregdate},
     '{escape_sql(member['mb_1'])}', '{escape_sql(member['mb_2'])}',
     '{escape_sql(member['mb_3'])}', '{escape_sql(member['mb_4'])}',
     '{escape_sql(member['mb_5'])}', '{escape_sql(member['mb_6'])}',
     '{escape_sql(member['mb_7'])}', '{escape_sql(member['mb_8'])}',
     '{escape_sql(member['mb_9'])}', '{escape_sql(member['mb_10'])}',
     'N', '')
    """

    if dry_run:
        return True

    return run_mysql_remote_update(query)

def update_board_member_idx(dry_run=True):
    """게시글의 mb_idx 업데이트 (mb_id로 매칭)"""
    print("\n게시글 회원 매칭 업데이트 중...")

    # 현재 회원 목록 조회
    members_query = "SELECT mb_idx, mb_id FROM zg_member"
    members_result = run_mysql_remote(members_query)

    member_map = {}
    if members_result:
        for line in members_result.split("\n"):
            if line.strip():
                parts = line.split("\t")
                if len(parts) >= 2:
                    member_map[parts[1]] = parts[0]  # mb_id -> mb_idx

    print(f"  회원 매핑 정보: {len(member_map)}명")

    total_updated = 0
    for board_id in BOARDS:
        table = f"zg_mod_board_data_{board_id}"

        # mb_id가 있지만 mb_idx가 0인 게시글 조회
        query = f"SELECT DISTINCT mb_id FROM {table} WHERE mb_id != '' AND mb_idx = 0"
        result = run_mysql_remote(query)

        if not result:
            continue

        for line in result.split("\n"):
            mb_id = line.strip()
            if not mb_id:
                continue

            if mb_id in member_map:
                mb_idx = member_map[mb_id]

                if dry_run:
                    print(f"  [{board_id}] mb_id={mb_id} -> mb_idx={mb_idx}")
                else:
                    update_query = f"UPDATE {table} SET mb_idx = {mb_idx} WHERE mb_id = '{escape_sql(mb_id)}'"
                    if run_mysql_remote_update(update_query):
                        print(f"  [OK] [{board_id}] mb_id={mb_id} -> mb_idx={mb_idx}")
                        total_updated += 1

    print(f"총 업데이트: {total_updated}개 게시판")

def main():
    import sys
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN - 실제 변경 없음")
        print("--execute 옵션으로 실행하면 실제 적용됩니다.")
        print("=" * 60)

    # 1. 회원 마이그레이션
    print("\n[1] 그누보드4 회원 데이터 조회 중...")
    members = get_g4_members()
    print(f"    총 {len(members)}명의 회원 발견")

    inserted = 0
    skipped = 0

    for member in members:
        existing = check_existing_member(member['mb_id'])

        if existing:
            print(f"  [SKIP] {member['mb_id']} ({member['mb_name']}) - 이미 존재 (mb_idx={existing})")
            skipped += 1
            continue

        print(f"  [ADD] {member['mb_id']} ({member['mb_name']}) - Level:{member['mb_level']}, Point:{member['mb_point']}")

        if not dry_run:
            if insert_member(member, dry_run=False):
                inserted += 1
            else:
                print(f"    [ERROR] 삽입 실패")
        else:
            inserted += 1

    print(f"\n회원 마이그레이션 결과: 추가 {inserted}명, 스킵 {skipped}명")

    # 2. 게시글 회원 매칭 업데이트
    print("\n[2] 게시글 회원 매칭 업데이트...")
    update_board_member_idx(dry_run=dry_run)

    if dry_run:
        print("\n" + "=" * 60)
        print("--execute 옵션으로 실행하면 실제 적용됩니다.")
        print("=" * 60)

if __name__ == "__main__":
    main()
