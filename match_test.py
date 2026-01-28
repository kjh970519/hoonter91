#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re

FILES_DIR = "/home/hoonter91/files"

def normalize_title(title):
    """제목을 파일명 매칭용으로 정규화"""
    normalized = title.replace(" ", "_")
    normalized = normalized.replace(".", "")
    normalized = normalized.replace("/", "")
    normalized = normalized.replace(":", "")
    normalized = normalized.replace("\t", "_")
    normalized = re.sub(r"_+", "_", normalized)
    normalized = normalized.rstrip("_")
    return normalized

def get_title_from_filename(filename):
    """파일명에서 제목 부분 추출"""
    name_without_ext = os.path.splitext(filename)[0]
    match = re.match(r"^(.+)_(\d+)$", name_without_ext)
    if match:
        return match.group(1), int(match.group(2))
    return name_without_ext, 0

# 파일 목록
files = os.listdir(FILES_DIR)
file_titles = {}
for f in files:
    title, seq = get_title_from_filename(f)
    if title not in file_titles:
        file_titles[title] = []
    file_titles[title].append({"filename": f, "seq": seq})

# 몇 가지 테스트
test_subjects = [
    "1999년 제1회 서울시동아리농구연맹 회장배 농구대회",
    "1973년 삼일중학교 시절 수학여행",
    "2009년도 육사 생도들과 수업 마치고 기념 촬영",
    "프로복싱 심판활동 하이라이트",
    "아버님 사진"
]

for subject in test_subjects:
    normalized = normalize_title(subject)
    print(f"제목: {subject}")
    print(f"정규화: {normalized}")
    
    # 매칭 찾기
    found = []
    for title, file_list in file_titles.items():
        if normalized == title or normalized in title or title in normalized:
            found.extend(file_list)
    
    if found:
        print(f"매칭된 파일: {len(found)}개")
        for f in sorted(found, key=lambda x: x["seq"]):
            print(f"  - {f[\"filename\"]}")
    else:
        print("매칭된 파일 없음")
    print()
