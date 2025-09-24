#!/bin/bash

# 버전 bump 스크립트
# 사용법: ./bump-version.sh [major|minor|patch]

# 현재 버전 읽기
CURRENT_VERSION=$(cat VERSION)

# 버전을 점(.)으로 분리
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# 인자에 따라 버전 증가
case "$1" in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        echo "🚀 Major 버전 업데이트: $CURRENT_VERSION → $MAJOR.$MINOR.$PATCH"
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        echo "✨ Minor 버전 업데이트: $CURRENT_VERSION → $MAJOR.$MINOR.$PATCH"
        ;;
    patch)
        PATCH=$((PATCH + 1))
        echo "🔧 Patch 버전 업데이트: $CURRENT_VERSION → $MAJOR.$MINOR.$PATCH"
        ;;
    *)
        echo "❌ 사용법: $0 [major|minor|patch]"
        echo "   major: x.0.0 (주요 변경, 호환성 깨짐)"
        echo "   minor: 0.x.0 (기능 추가, 호환성 유지)"
        echo "   patch: 0.0.x (버그 수정)"
        exit 1
        ;;
esac

# 새 버전
NEW_VERSION="$MAJOR.$MINOR.$PATCH"

# VERSION 파일 업데이트
echo "$NEW_VERSION" > VERSION

# update-version.sh 실행하여 모든 파일 업데이트
$(dirname "$0")/update-version.sh

echo "✅ 버전이 $NEW_VERSION으로 업데이트되었습니다!"
echo ""
echo "다음 단계:"
echo "  1. 변경사항 확인: git diff"
echo "  2. 커밋: git add -A && git commit -m \"chore: bump version to v$NEW_VERSION\""
echo "  3. 태그 추가: git tag -a v$NEW_VERSION -m \"Release v$NEW_VERSION\""
echo "  4. 푸시: git push && git push --tags"