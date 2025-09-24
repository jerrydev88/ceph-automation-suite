#!/bin/bash

# VERSION 파일에서 버전 읽기
VERSION=$(cat VERSION)

echo "📦 버전을 $VERSION으로 업데이트 중..."

# pyproject.toml 업데이트
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
else
    # Linux
    sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
fi

# Dockerfile 업데이트 (ARG와 LABEL 모두)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/^ARG VERSION=.*/ARG VERSION=$VERSION/" Dockerfile
    sed -i '' "s/^LABEL version=.*/LABEL version=\"$VERSION\"/" Dockerfile
else
    sed -i "s/^ARG VERSION=.*/ARG VERSION=$VERSION/" Dockerfile
    sed -i "s/^LABEL version=.*/LABEL version=\"$VERSION\"/" Dockerfile
fi

# README.md 업데이트
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/^\*\*버전\*\*:.*/\*\*버전\*\*: $VERSION/" README.md
else
    sed -i "s/^\*\*버전\*\*:.*/\*\*버전\*\*: $VERSION/" README.md
fi

echo "✅ 버전 업데이트 완료!"
echo "   - pyproject.toml"
echo "   - Dockerfile"
echo "   - README.md"