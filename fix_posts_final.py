#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1. 잘못 매칭된 첨부파일 제거
2. 다운로드 횟수 매칭
3. 링크 데이터를 본문에 추가 (클릭횟수 포함)
"""
import subprocess
import re

# 그누보드4 게시판 ID -> Zigger 게시판 ID 매핑
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

ZIGGER_BOARDS = [
    "story_album", "story_basketball", "story_boxing", "story_family",
    "story_julye", "story_sports_video", "bucheon_college", "military_academy",
    "youth_sports", "lecture_career", "jinyong_free", "community_notice",
    "community_free", "community_pds", "community_qna"
]

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
    if result.returncode != 0 and "ERROR" in result.stderr:
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


def remove_orphan_files(dry_run=True):
    """본문에 없는 첨부파일 제거 (이미지 파일만)"""
    print("\n[1] 잘못 매칭된 첨부파일 제거...")

    total_removed = 0

    for board_id in ZIGGER_BOARDS:
        # 첨부파일이 있는 게시글 조회
        query = f"""
        SELECT DISTINCT f.data_idx, f.idx as file_idx, f.file_name, d.article
        FROM zg_mod_board_files f
        JOIN zg_mod_board_data_{board_id} d ON d.idx = f.data_idx
        WHERE f.id = '{board_id}'
        """
        result = run_mysql_remote(query)

        if not result:
            continue

        for line in result.split("\n"):
            if not line.strip():
                continue

            parts = line.split("\t")
            if len(parts) < 4:
                continue

            data_idx = parts[0]
            file_idx = parts[1]
            file_name = parts[2]
            article = parts[3] if len(parts) > 3 else ""

            # 이미지 파일인 경우만 체크
            if not is_image(file_name):
                continue

            # 본문에 해당 파일이 있는지 확인
            if file_name in article:
                continue  # 본문에 있으면 유지

            # 본문에 없는 이미지 파일 제거
            print(f"    [{board_id}] idx={data_idx}: 고아 파일 제거 - {file_name[:40]}...")

            if not dry_run:
                delete_query = f"DELETE FROM zg_mod_board_files WHERE idx = {file_idx}"
                if run_mysql_remote_update(delete_query):
                    total_removed += 1

    print(f"\n  총 {total_removed}개 고아 파일 제거")


def update_download_counts(dry_run=True):
    """다운로드 횟수 업데이트"""
    print("\n[2] 다운로드 횟수 업데이트...")

    total_updated = 0

    for g4_board, zg_board in BOARD_MAP.items():
        # 다운로드 횟수가 있는 파일 조회
        query = f"""
        SELECT w.wr_id, w.wr_subject, f.bf_no, f.bf_source, f.bf_download
        FROM g4_write_{g4_board} w
        JOIN g4_board_file f ON f.bo_table = '{g4_board}' AND f.wr_id = w.wr_id
        WHERE f.bf_download > 0
        """
        result = run_mysql_local(query)

        if not result:
            continue

        for line in result.split("\n"):
            if not line.strip():
                continue

            parts = line.split("\t")
            if len(parts) < 5:
                continue

            wr_id = parts[0]
            wr_subject = parts[1]
            bf_no = parts[2]
            bf_source = parts[3]
            bf_download = parts[4]

            # zigger에서 해당 게시글 찾기
            zg_query = f"SELECT idx FROM zg_mod_board_data_{zg_board} WHERE subject = '{escape_sql(wr_subject)}' LIMIT 1"
            zg_idx = run_mysql_remote(zg_query)

            if not zg_idx:
                continue

            # 해당 파일의 file_cnt 업데이트 (file_seq로 매칭)
            file_seq = int(bf_no) + 1
            update_query = f"UPDATE zg_mod_board_files SET file_cnt = {bf_download} WHERE id = '{zg_board}' AND data_idx = {zg_idx} AND file_seq = {file_seq}"

            if dry_run:
                print(f"    [{zg_board}] idx={zg_idx}: {bf_source} -> 다운로드 {bf_download}회")
            else:
                if run_mysql_remote_update(update_query):
                    print(f"    [{zg_board}] idx={zg_idx}: {bf_source} -> 다운로드 {bf_download}회")
                    total_updated += 1

    print(f"\n  총 {total_updated}개 다운로드 횟수 업데이트")


def add_links_to_articles(dry_run=True):
    """링크 데이터를 본문에 추가"""
    print("\n[3] 링크 데이터 본문에 추가...")

    total_updated = 0

    for g4_board, zg_board in BOARD_MAP.items():
        # 링크가 있는 게시글 조회
        query = f"""
        SELECT wr_id, wr_subject, wr_link1, wr_link1_hit, wr_link2, wr_link2_hit
        FROM g4_write_{g4_board}
        WHERE LENGTH(wr_link1) > 0 OR LENGTH(wr_link2) > 0
        """
        result = run_mysql_local(query)

        if not result:
            continue

        for line in result.split("\n"):
            if not line.strip():
                continue

            parts = line.split("\t")
            if len(parts) < 6:
                continue

            wr_id = parts[0]
            wr_subject = parts[1]
            wr_link1 = parts[2] if parts[2] else ""
            wr_link1_hit = parts[3] if parts[3] else "0"
            wr_link2 = parts[4] if parts[4] else ""
            wr_link2_hit = parts[5] if parts[5] else "0"

            # zigger에서 해당 게시글 찾기
            zg_query = f"SELECT idx, article FROM zg_mod_board_data_{zg_board} WHERE subject = '{escape_sql(wr_subject)}' LIMIT 1"
            zg_result = run_mysql_remote(zg_query)

            if not zg_result:
                continue

            zg_parts = zg_result.split("\t", 1)
            zg_idx = zg_parts[0]
            current_article = zg_parts[1] if len(zg_parts) > 1 else ""

            # 이미 링크가 추가되어 있는지 확인
            if "관련 링크" in current_article:
                continue

            # 링크 HTML 생성
            link_html = ""
            if wr_link1:
                link_html += f'<p><strong>관련 링크 1:</strong> <a href="{wr_link1}" target="_blank">{wr_link1}</a>'
                if int(wr_link1_hit) > 0:
                    link_html += f' (클릭 {wr_link1_hit}회)'
                link_html += '</p>'

            if wr_link2:
                link_html += f'<p><strong>관련 링크 2:</strong> <a href="{wr_link2}" target="_blank">{wr_link2}</a>'
                if int(wr_link2_hit) > 0:
                    link_html += f' (클릭 {wr_link2_hit}회)'
                link_html += '</p>'

            if not link_html:
                continue

            # 본문 맨 위에 링크 추가
            link_section = f'<div class="legacy-links" style="background:#f5f5f5;padding:10px;margin-bottom:15px;border-radius:5px;">{link_html}</div>'

            print(f"    [{zg_board}] idx={zg_idx}: 링크 추가")
            if wr_link1:
                print(f"        링크1: {wr_link1[:50]}... (클릭 {wr_link1_hit}회)")
            if wr_link2:
                print(f"        링크2: {wr_link2[:50]}... (클릭 {wr_link2_hit}회)")

            if not dry_run:
                update_query = f"UPDATE zg_mod_board_data_{zg_board} SET article = CONCAT('{escape_sql(link_section)}', article) WHERE idx = {zg_idx}"
                if run_mysql_remote_update(update_query):
                    total_updated += 1

    print(f"\n  총 {total_updated}개 게시글에 링크 추가")


def main():
    import sys
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN - 실제 변경 없음")
        print("--execute 옵션으로 실행하면 실제 적용됩니다.")
        print("=" * 60)

    # 1. 잘못 매칭된 첨부파일 제거
    remove_orphan_files(dry_run=dry_run)

    # 2. 다운로드 횟수 업데이트
    update_download_counts(dry_run=dry_run)

    # 3. 링크 데이터 추가
    add_links_to_articles(dry_run=dry_run)

    if dry_run:
        print("\n" + "=" * 60)
        print("--execute 옵션으로 실행하면 실제 적용됩니다.")
        print("=" * 60)


if __name__ == "__main__":
    main()
