#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import subprocess
import shutil
import hashlib
from datetime import datetime

FILES_DIR = "/home/hoonter91/files"
THUMBS_DIR = "/home/hoonter91/thumbs"
WWW_DATA_PATH = "/home/hoonter91/www/data/board"

IMAGE_EXTS = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "jfif"]

BOARDS = [
    "story_album", "story_basketball", "story_boxing", "story_family",
    "story_julye", "story_sports_video", "bucheon_college", "military_academy",
    "youth_sports", "lecture_career", "jinyong_free", "community_notice",
    "community_free", "community_pds", "community_qna"
]

def run_mysql(query):
    cmd = ["docker", "exec", "mysql56_db", "mysql", "-u", "hoonter91", "-phoon45789", "hoonter91", "-N", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def run_mysql_update(query):
    cmd = ["docker", "exec", "mysql56_db", "mysql", "-u", "hoonter91", "-phoon45789", "hoonter91", "-e", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("MySQL Error:", result.stderr)
    return result.returncode == 0

def normalize_title(title):
    normalized = title.replace(" ", "_")
    normalized = normalized.replace(".", "")
    normalized = normalized.replace("/", "")
    normalized = normalized.replace(":", "")
    normalized = normalized.replace("\t", "_")
    normalized = normalized.replace("'", "")
    # Remove view count pattern
    normalized = re.sub(r"_*조회수_*\d+", "", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    normalized = normalized.rstrip("_")
    return normalized

def get_title_from_filename(filename):
    name_without_ext = os.path.splitext(filename)[0]
    # Remove sequence number at the end
    pattern = r"^(.+)_(\d+)$"
    match = re.match(pattern, name_without_ext)
    if match:
        title_part = match.group(1)
        seq = int(match.group(2))
    else:
        title_part = name_without_ext
        seq = 0

    # Remove view count from title
    title_part = re.sub(r"_*조회수_*\d+", "", title_part)
    title_part = re.sub(r"_+", "_", title_part)
    title_part = title_part.rstrip("_")
    return title_part, seq

def get_ext(filename):
    return os.path.splitext(filename)[1].lstrip(".").lower()

def is_image(filename):
    return get_ext(filename) in IMAGE_EXTS

def gen_hash_filename(orig, idx=0):
    ts = hashlib.md5((str(datetime.now()) + str(idx)).encode()).hexdigest()
    ts += hashlib.md5(orig.encode()).hexdigest()
    return ts + str(idx) + "N." + get_ext(orig)

def get_all_posts():
    posts = []
    for board_id in BOARDS:
        table = "zg_mod_board_data_" + board_id
        query = "SELECT idx, subject, article FROM " + table
        result = run_mysql(query)
        if result:
            for line in result.split("\n"):
                parts = line.split("\t")
                if len(parts) >= 2:
                    idx = parts[0]
                    subject = parts[1]
                    article = parts[2] if len(parts) > 2 else ""
                    posts.append({
                        "board_id": board_id,
                        "idx": idx,
                        "subject": subject,
                        "article": article
                    })
    return posts

def get_file_titles():
    files = os.listdir(FILES_DIR)
    file_titles = {}
    for f in files:
        title, seq = get_title_from_filename(f)
        if title not in file_titles:
            file_titles[title] = []
        file_titles[title].append({"filename": f, "seq": seq})
    return file_titles

def match_post_to_files(post, file_titles):
    normalized = normalize_title(post["subject"])
    found = []

    for title, file_list in file_titles.items():
        # Exact match or contains
        if normalized == title:
            found.extend(file_list)
        elif len(normalized) > 15 and len(title) > 15:
            # Check if significant part matches
            if normalized in title or title in normalized:
                found.extend(file_list)
            # Check prefix match (first 20 chars)
            elif normalized[:20] == title[:20]:
                found.extend(file_list)

    return sorted(found, key=lambda x: x["seq"])

def escape_sql(s):
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace('"', '\\"')
    return s

def process_post(post, matched_files, dry_run=True):
    board_id = post["board_id"]
    post_idx = post["idx"]

    subject_short = post["subject"][:40] if len(post["subject"]) > 40 else post["subject"]
    print("\n[" + board_id + "] idx=" + post_idx + ": " + subject_short + "...")

    if not matched_files:
        print("  No matched files")
        return

    upload_dir = datetime.now().strftime("%Y%m")
    target_dir = os.path.join(WWW_DATA_PATH, board_id, upload_dir)
    thumb_dir = os.path.join(target_dir, "thumb")

    images_html = []
    file_seq = 1
    first_image_hash = None  # 첫 번째 이미지 파일명 저장용
    has_image = False

    for f in matched_files:
        filename = f["filename"]
        is_img = is_image(filename)

        file_type = "[IMG]" if is_img else "[FILE]"
        print("  " + file_type + " " + filename)

        if dry_run:
            continue

        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)

        src_path = os.path.join(FILES_DIR, filename)
        if not os.path.exists(src_path):
            print("    [!] File not found")
            continue

        hash_name = gen_hash_filename(filename, file_seq)
        dst_path = os.path.join(target_dir, hash_name)

        shutil.copy2(src_path, dst_path)
        file_size = os.path.getsize(src_path)

        filepath = "/board/" + board_id + "/" + upload_dir
        esc_orig = escape_sql(filename)
        query = "INSERT INTO zg_dataupload (filepath, orgfile, repfile, storage, byte, regdate) VALUES ('" + filepath + "', '" + esc_orig + "', '" + hash_name + "', 'N', " + str(file_size) + ", NOW())"
        run_mysql_update(query)

        # 모든 파일(이미지 포함)을 zg_mod_board_files에 등록
        query = "INSERT INTO zg_mod_board_files (id, data_idx, file_seq, file_name, regdate) VALUES ('" + board_id + "', " + post_idx + ", " + str(file_seq) + ", '" + hash_name + "', NOW())"
        run_mysql_update(query)

        if is_img:
            has_image = True
            # 첫 번째 이미지 파일명 저장 (file2용)
            if first_image_hash is None:
                first_image_hash = hash_name

            thumb_src = os.path.join(THUMBS_DIR, filename)
            if os.path.exists(thumb_src):
                shutil.copy2(thumb_src, os.path.join(thumb_dir, hash_name))

            img_url = "/data/board/" + board_id + "/" + upload_dir + "/" + hash_name
            images_html.append('<p><img src="' + img_url + '" alt="" style="max-width:100%;" /></p>')

        file_seq += 1

    if not dry_run:
        # file1, file2 업데이트
        table = "zg_mod_board_data_" + board_id
        if has_image and first_image_hash:
            query = "UPDATE " + table + " SET file1 = 'image', file2 = '" + first_image_hash + "' WHERE idx = " + post_idx
            run_mysql_update(query)
            print("  [OK] Updated file1='image', file2='" + first_image_hash[:20] + "...'")
        elif file_seq > 1:
            # 이미지가 없고 일반 파일만 있는 경우
            query = "UPDATE " + table + " SET file1 = 'file' WHERE idx = " + post_idx
            run_mysql_update(query)
            print("  [OK] Updated file1='file'")

        # 본문에 이미지 추가
        if images_html:
            new_content = "".join(images_html)
            esc_content = escape_sql(new_content)
            query = "UPDATE " + table + " SET article = CONCAT(IFNULL(article,''), '" + esc_content + "') WHERE idx = " + post_idx
            run_mysql_update(query)
            print("  [OK] Added " + str(len(images_html)) + " images to article")

def main():
    import sys
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN - No actual changes will be made.")
        print("Run with --execute to apply changes.")
        print("=" * 60)

    file_titles = get_file_titles()
    print("\nFile groups in files dir: " + str(len(file_titles)))

    posts = get_all_posts()
    print("Total posts: " + str(len(posts)))

    matched_count = 0
    for post in posts:
        matched = match_post_to_files(post, file_titles)
        if matched:
            matched_count += 1
            process_post(post, matched, dry_run=dry_run)

    print("\nMatched posts: " + str(matched_count))

    if dry_run:
        print("\nRun with --execute to apply changes.")

if __name__ == "__main__":
    main()
