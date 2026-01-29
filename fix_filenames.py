#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1. 그누보드4 원본 파일명을 zigger DB에 매칭
2. 본문에 이미지가 있는 경우 zg_mod_board_files에서 이미지 파일 제거 (중복 방지)
"""
import subprocess
import re

# 그누보드4 게시판 ID -> Zigger 게시판 ID 매핑
BOARD_MAP = {
    "uvrypoe53c": "story_album",           # 김재훈의 추억앨범
    "sq5bz63vib": "story_basketball",      # 서울특별시동아리농구연맹
    "product": "story_boxing",             # 육군사관학교(복싱부) - 복싱
    "hmfhrc2smz": "story_family",          # 김재훈의 가족신문스크랩
    "a7995k6o7w": "story_julye",           # 주례 히스토리
    "gkyrbxkmr4": "story_sports_video",    # 김재훈의 스포츠동영상
    "FAQ": "bucheon_college",              # 부천대학교
    "33csifbbx7": "jinyong_free",          # 김진용
    "yjye2kq2yu": "youth_sports",          # 김정용&김진용 농구이야기
    "nudi15j5qw": "lecture_career",        # 진로 특강
    "news": "community_notice",            # 뉴스&공지
    "pds": "community_pds",                # 프로복싱(국제심판)
    "QNA": "community_qna",                # 묻고답하기
    "oadi40dw8d": "community_free",        # 김재훈의 사진 자료실
    "d7idk8k5tz": "story_family",          # 가족신문스크랩 (중복)
}

IMAGE_EXTS = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "jfif"]

def run_mysql_local(query):
    """로컬 MySQL (백업 DB) 쿼리"""
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "root", "-p1234",
           "--default-character-set=utf8", "hoonter91_backup", "-N", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def run_mysql_remote(query):
    """원격 MySQL (운영 DB) 쿼리"""
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "hoonter91", "-phoon45789",
           "-h", "49.50.129.138", "--default-character-set=utf8", "hoonter91", "-N", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def run_mysql_remote_update(query):
    """원격 MySQL UPDATE"""
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "hoonter91", "-phoon45789",
           "-h", "49.50.129.138", "--default-character-set=utf8", "hoonter91", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and "ERROR" in result.stderr:
        print(f"    [ERROR] {result.stderr.split('ERROR')[1][:100]}")
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

def get_ext(filename):
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

def is_image(filename):
    return get_ext(filename) in IMAGE_EXTS

def fix_filenames(dry_run=True):
    """그누보드4 원본 파일명을 zigger에 매칭"""
    print("\n[1] 원본 파일명 매칭...")

    total_updated = 0

    for g4_board, zg_board in BOARD_MAP.items():
        # 그누보드4 게시글-파일 정보 조회
        query = f"""
        SELECT w.wr_id, w.wr_subject, f.bf_no, f.bf_source, f.bf_file
        FROM g4_write_{g4_board} w
        LEFT JOIN g4_board_file f ON f.bo_table='{g4_board}' AND f.wr_id=w.wr_id
        WHERE f.bf_source != ''
        ORDER BY w.wr_id, f.bf_no
        """
        result = run_mysql_local(query)

        if not result:
            continue

        print(f"\n  [{g4_board} -> {zg_board}]")

        for line in result.split("\n"):
            if not line.strip():
                continue

            parts = line.split("\t")
            if len(parts) < 5:
                continue

            g4_wr_id = parts[0]
            g4_subject = parts[1]
            bf_no = parts[2]
            bf_source = parts[3]  # 원본 파일명
            bf_file = parts[4]    # 저장된 파일명

            # zigger에서 같은 제목의 게시글 찾기
            zg_query = f"SELECT idx FROM zg_mod_board_data_{zg_board} WHERE subject = '{escape_sql(g4_subject)}' LIMIT 1"
            zg_idx = run_mysql_remote(zg_query)

            if not zg_idx:
                continue

            # zg_mod_board_files에서 파일 찾기
            file_query = f"SELECT file_name FROM zg_mod_board_files WHERE id='{zg_board}' AND data_idx={zg_idx} AND file_seq={int(bf_no)+1}"
            zg_file = run_mysql_remote(file_query)

            if not zg_file:
                continue

            # zg_dataupload에서 orgfile 업데이트
            print(f"    wr_id={g4_wr_id} -> idx={zg_idx}: {bf_source}")

            if not dry_run:
                update_query = f"UPDATE zg_dataupload SET orgfile = '{escape_sql(bf_source)}' WHERE repfile = '{escape_sql(zg_file)}'"
                if run_mysql_remote_update(update_query):
                    total_updated += 1

    print(f"\n  총 {total_updated}개 파일명 업데이트")

def remove_duplicate_images(dry_run=True):
    """본문에 이미지가 있는 게시글의 zg_mod_board_files에서 이미지 제거"""
    print("\n[2] 중복 이미지 제거...")

    boards = [
        "story_album", "story_basketball", "story_boxing", "story_family",
        "story_julye", "story_sports_video", "bucheon_college", "military_academy",
        "youth_sports", "lecture_career", "jinyong_free", "community_notice",
        "community_free", "community_pds", "community_qna"
    ]

    total_removed = 0

    for board_id in boards:
        # 본문에 이미지가 있는 게시글 조회
        query = f"SELECT idx, article FROM zg_mod_board_data_{board_id} WHERE article LIKE '%<img%'"
        result = run_mysql_remote(query)

        if not result:
            continue

        for line in result.split("\n"):
            if not line.strip():
                continue

            parts = line.split("\t", 1)
            if len(parts) < 2:
                continue

            idx = parts[0]
            article = parts[1]

            # 본문에서 이미지 파일명 추출
            pattern = r'/data/board/' + re.escape(board_id) + r'/\d+/([a-f0-9]+[NY]\.[a-zA-Z]+)'
            img_files = re.findall(pattern, article)

            if not img_files:
                continue

            # zg_mod_board_files에서 본문에 있는 이미지 파일 삭제
            for img_file in img_files:
                if is_image(img_file):
                    check_query = f"SELECT idx FROM zg_mod_board_files WHERE id='{board_id}' AND data_idx={idx} AND file_name='{escape_sql(img_file)}'"
                    file_idx = run_mysql_remote(check_query)

                    if file_idx:
                        print(f"    [{board_id}] idx={idx}: 중복 이미지 제거 - {img_file[:30]}...")

                        if not dry_run:
                            delete_query = f"DELETE FROM zg_mod_board_files WHERE idx={file_idx}"
                            if run_mysql_remote_update(delete_query):
                                total_removed += 1

    print(f"\n  총 {total_removed}개 중복 이미지 제거")

def main():
    import sys
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN - 실제 변경 없음")
        print("--execute 옵션으로 실행하면 실제 적용됩니다.")
        print("=" * 60)

    # 1. 원본 파일명 매칭
    fix_filenames(dry_run=dry_run)

    # 2. 중복 이미지 제거
    remove_duplicate_images(dry_run=dry_run)

    if dry_run:
        print("\n" + "=" * 60)
        print("--execute 옵션으로 실행하면 실제 적용됩니다.")
        print("=" * 60)

if __name__ == "__main__":
    main()
