#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존에 마이그레이션된 데이터의 file1, file2 필드와 zg_mod_board_files 테이블을 수정하는 스크립트
"""
import os
import re
import subprocess

IMAGE_EXTS = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "jfif"]

BOARDS = [
    "story_album", "story_basketball", "story_boxing", "story_family",
    "story_julye", "story_sports_video", "bucheon_college", "military_academy",
    "youth_sports", "lecture_career", "jinyong_free", "community_notice",
    "community_free", "community_pds", "community_qna"
]

def run_mysql(query):
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "hoonter91", "-phoon45789", "-h", "49.50.129.138", "hoonter91", "-N", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("MySQL Query Error:", result.stderr)
    return result.stdout.strip()

def run_mysql_update(query):
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "hoonter91", "-phoon45789", "-h", "49.50.129.138", "hoonter91", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("MySQL Error:", result.stderr)
    return result.returncode == 0

def get_ext(filename):
    return os.path.splitext(filename)[1].lstrip(".").lower()

def is_image(filename):
    return get_ext(filename) in IMAGE_EXTS

def escape_sql(s):
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace('"', '\\"')
    return s

def fix_board_data(board_id, dry_run=True):
    """게시글의 file1, file2 필드 수정 및 zg_mod_board_files 등록"""
    table = "zg_mod_board_data_" + board_id

    # 본문에 이미지가 있지만 file2가 NULL인 게시글 조회
    query = f"SELECT idx, article FROM {table} WHERE article LIKE '%<img%' AND (file2 IS NULL OR file2 = '')"
    result = run_mysql(query)

    if not result:
        print(f"[{board_id}] No posts to fix")
        return

    fixed_count = 0
    for line in result.split("\n"):
        if not line.strip():
            continue

        parts = line.split("\t", 1)
        if len(parts) < 2:
            continue

        idx = parts[0]
        article = parts[1] if len(parts) > 1 else ""

        # 본문에서 이미지 파일명 추출
        # 패턴: /data/board/board_id/yyyymm/filename.ext
        pattern = r'/data/board/' + re.escape(board_id) + r'/(\d+)/([a-f0-9]+[NY]\.[a-zA-Z]+)'
        matches = re.findall(pattern, article)

        if not matches:
            continue

        # 첫 번째 이미지 파일명
        first_match = matches[0]
        upload_dir = first_match[0]  # yyyymm
        first_image = first_match[1]  # 해시파일명

        print(f"  [{board_id}] idx={idx}: Found {len(matches)} images, first={first_image[:30]}...")

        if dry_run:
            continue

        # file1, file2 업데이트
        query = f"UPDATE {table} SET file1 = 'image', file2 = '{escape_sql(first_image)}' WHERE idx = {idx}"
        if run_mysql_update(query):
            print(f"    [OK] Updated file1, file2")

        # zg_mod_board_files에 이미지 파일 등록 (중복 체크)
        file_seq = 1
        for match in matches:
            img_file = match[1]

            # 이미지 파일인지 확인
            if not is_image(img_file):
                continue

            # 이미 등록되어 있는지 확인
            check_query = f"SELECT COUNT(*) FROM zg_mod_board_files WHERE id='{board_id}' AND data_idx={idx} AND file_name='{escape_sql(img_file)}'"
            count = run_mysql(check_query)

            if count and int(count) > 0:
                print(f"    [SKIP] Already exists: {img_file[:30]}...")
                continue

            # 등록
            insert_query = f"INSERT INTO zg_mod_board_files (id, data_idx, file_seq, file_name, regdate) VALUES ('{board_id}', {idx}, {file_seq}, '{escape_sql(img_file)}', NOW())"
            if run_mysql_update(insert_query):
                print(f"    [OK] Registered file: {img_file[:30]}...")

            file_seq += 1

        fixed_count += 1

    print(f"[{board_id}] Fixed {fixed_count} posts")

def main():
    import sys
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN - No actual changes will be made.")
        print("Run with --execute to apply changes.")
        print("=" * 60)

    for board_id in BOARDS:
        print(f"\nProcessing board: {board_id}")
        fix_board_data(board_id, dry_run=dry_run)

    if dry_run:
        print("\n" + "=" * 60)
        print("Run with --execute to apply changes.")
        print("=" * 60)

if __name__ == "__main__":
    main()
