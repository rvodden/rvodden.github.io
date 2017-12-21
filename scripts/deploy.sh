#!/bin/bash
set -eux pipefail

# Variables
ORIGIN_URL=$(git config --get remote.origin.url 2>&1)

if [ -n ${?}  ]; then
    echo "Failed to get origin URL"
    echo $ORIGIN_URL
    exit -1
fi

# Trust github
mkdir -p ~/.ssh
echo <<EOF >> ~/.ssh/known_hosts
github.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==
EOF

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
git push -f $ORIGIN_URL master

# Move back to previous branch.
git checkout -

echo "Deployed Successfully!"

exit 0
