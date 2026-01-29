#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1. 모든 첨부파일의 원본 파일명을 그누보드4 데이터로 업데이트
2. 이미지를 본문 앞에 배치하도록 변경
"""
import subprocess
import re

BOARD_MAP = {
    "uvrypoe53c": "story_album",
    "sq5bz63vib": "story_basketball",
    "product": "story_boxing",
    "hmfhrc2smz": "story_family",
    "a7995k6o7w": "story_julye",
    "gkyrbxkmr4": "story_sports_video",
    "FAQ": "bucheon_college",
    "33csifbbx7": "jinyong_free",
    "yjye2kq2yu": "youth_sports",
    "nudi15j5qw": "lecture_career",
    "news": "community_notice",
    "pds": "community_pds",
    "QNA": "community_qna",
    "oadi40dw8d": "community_free",
    "d7idk8k5tz": "story_family",
    "sahjtudkhj": "bucheon_college",
    "91kf6ceh0j": "community_free",
}

IMAGE_EXTS = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "jfif"]

def run_mysql_local(query):
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "root", "-p1234",
           "--default-character-set=utf8", "hoonter91_backup", "-N", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def run_mysql_remote(query):
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "hoonter91", "-phoon45789",
           "-h", "49.50.129.138", "--default-character-set=utf8", "hoonter91", "-N", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def run_mysql_remote_update(query):
    cmd = ["docker", "exec", "mysql57", "mysql", "-u", "hoonter91", "-phoon45789",
           "-h", "49.50.129.138", "--default-character-set=utf8", "hoonter91", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def escape_sql(s):
    if s is None:
        return ""
    s = str(s)
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace('"', '\\"')
    return s

def is_image(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in IMAGE_EXTS


def fix_all_filenames(dry_run=True):
    """모든 첨부파일의 원본 파일명 업데이트"""
    print("\n[1] 첨부파일 원본 파일명 업데이트...")

    total_updated = 0

    for g4_board, zg_board in BOARD_MAP.items():
        # 그누보드4에서 게시글과 첨부파일 정보 조회
        query = f"""
        SELECT w.wr_id, w.wr_subject, f.bf_no, f.bf_source
        FROM g4_write_{g4_board} w
        JOIN g4_board_file f ON f.bo_table = '{g4_board}' AND f.wr_id = w.wr_id
        WHERE f.bf_source IS NOT NULL AND f.bf_source != ''
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
            if len(parts) < 4:
                continue

            wr_id = parts[0]
            wr_subject = parts[1]
            bf_no = int(parts[2])
            bf_source = parts[3]  # 원본 파일명

            # zigger에서 해당 게시글 찾기
            zg_query = f"SELECT idx FROM zg_mod_board_data_{zg_board} WHERE subject = '{escape_sql(wr_subject)}' LIMIT 1"
            zg_idx = run_mysql_remote(zg_query)

            if not zg_idx:
                continue

            # zg_mod_board_files에서 파일 찾기 (file_seq = bf_no + 1)
            file_seq = bf_no + 1
            file_query = f"SELECT file_name FROM zg_mod_board_files WHERE id='{zg_board}' AND data_idx={zg_idx} AND file_seq={file_seq}"
            zg_file = run_mysql_remote(file_query)

            if not zg_file:
                continue

            # 현재 orgfile 확인
            current_query = f"SELECT orgfile FROM zg_dataupload WHERE repfile='{escape_sql(zg_file)}'"
            current_orgfile = run_mysql_remote(current_query)

            if current_orgfile == bf_source:
                continue  # 이미 올바른 파일명

            print(f"    idx={zg_idx}, seq={file_seq}: {current_orgfile[:40]}... -> {bf_source[:40]}...")

            if not dry_run:
                update_query = f"UPDATE zg_dataupload SET orgfile = '{escape_sql(bf_source)}' WHERE repfile = '{escape_sql(zg_file)}'"
                if run_mysql_remote_update(update_query):
                    total_updated += 1

    print(f"\n  총 {total_updated}개 파일명 업데이트")


def fix_image_position(dry_run=True):
    """이미지를 본문 앞으로 이동"""
    print("\n[2] 이미지 위치 수정 (본문 앞으로 이동)...")

    total_updated = 0

    zigger_boards = list(set(BOARD_MAP.values()))

    for zg_board in zigger_boards:
        # 본문에 이미지가 있는 게시글 조회
        query = f"SELECT idx, article FROM zg_mod_board_data_{zg_board} WHERE article LIKE '%<img%'"
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

            # 이미지 태그 추출 (본문 끝에 있는 이미지들)
            # 패턴: <p><img src="..." ... /></p> 형태
            img_pattern = r'(<p><img[^>]+/></p>)'
            img_matches = re.findall(img_pattern, article)

            if not img_matches:
                continue

            # 이미지가 본문 끝에 있는지 확인
            # 본문에서 이미지 태그들을 제거
            text_without_images = re.sub(img_pattern, '', article).strip()

            # 이미지가 이미 앞에 있으면 스킵
            if article.strip().startswith('<p><img'):
                continue

            # 이미지를 본문 앞으로 이동
            images_html = ''.join(img_matches)
            new_article = images_html + text_without_images

            print(f"    [{zg_board}] idx={idx}: 이미지 {len(img_matches)}개 앞으로 이동")

            if not dry_run:
                update_query = f"UPDATE zg_mod_board_data_{zg_board} SET article = '{escape_sql(new_article)}' WHERE idx = {idx}"
                if run_mysql_remote_update(update_query):
                    total_updated += 1

    print(f"\n  총 {total_updated}개 게시글 이미지 위치 수정")


def main():
    import sys
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN - 실제 변경 없음")
        print("--execute 옵션으로 실행하면 실제 적용됩니다.")
        print("=" * 60)

    # 1. 첨부파일 원본 파일명 업데이트
    fix_all_filenames(dry_run=dry_run)

    # 2. 이미지 위치 수정
    fix_image_position(dry_run=dry_run)

    if dry_run:
        print("\n" + "=" * 60)
        print("--execute 옵션으로 실행하면 실제 적용됩니다.")
        print("=" * 60)


if __name__ == "__main__":
    main()
