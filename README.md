
# Tired of Resource OverlaYs


### Note to developers:

The development branch is `devel`, all developers should branch off 'devel' when
implementing new features.  Feature branches are named `feature/xyz`, and are
only merged into devel after coordinating with the other developers.

Releases are tagged on the `master` branch -- only the release manager will merge
from `devel` to `master`, to prepare for a release.

An usual workflow should look like:

```
git clone git@github.com:saga-project/troy.git # get repostory
cd troy                                        # 
git checkout devel                             # switch to devel branch
git checkout -b feature/world_domination       # create a feature branch from there
vim troy/world_domination.py                   # do the deed...
vim tests/test_world_domination.py             #
git commit -am 'we now dominate the world'     # commit your changes
git push origin feature/world_domination       # sync with github
```

The last command will ensure that your (until then only locally existing) branch
will be mirrored in the central repository, and is available for other
developers.

Once the group agreed on merging, you would run:

```
git checkout devel
git pull                               # get updates from github
git checkout feature/world_domination
git pull                               # get updates from github
git merge devel                        # make sure branch is in sync with devel
run_my_tests                           # do it!
git checkout devel
git merge feature/world_domination     # merge your feature branch
git push origin                        # sync with github
git branch -d feature/world_domination # remove feature branch
```

If unsure about anything, as Andre ;)

