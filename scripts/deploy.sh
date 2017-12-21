#!/bin/bash
set -eux pipefail

# Variables
ORIGIN_URL=$(git config --get remote.origin.url 2>&1)

if [ 0 -ne ${?}  ]; then
    echo "Failed to get origin URL"
    echo $ORIGIN_URL
    exit -1
fi

mkdir -p ~/.ssh
ssh-keyscan github.com >> ~/.ssh/known_hosts

echo "Started deploying"

# Checkout new master branch.
if [ `git branch | grep master` ]
then
  git branch -D master
fi
git checkout -b master

# Delete and move files.
find . -maxdepth 1 ! -name .circleci ! -name '_site' ! -name '.git' ! -name '.gitignore' -exec rm -rf {} \;
mv _site/* .
rm -R _site/

# Push to gh-pages.
git config user.name "$USER_NAME"
git config user.email "$USER_EMAIL"

echo "vodden.com" > CNAME

git add -fA
git commit --allow-empty -m "$(git log -1 --pretty=%B) [ci skip]"
git push --no-verify -f $ORIGIN_URL master

# Move back to previous branch.
git checkout -

echo "Deployed Successfully!"

exit 0
