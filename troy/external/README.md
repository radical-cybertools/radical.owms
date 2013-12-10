
This `external` subtree contains copies of, well, external packages -- most
importantly the `bundle` module from the aims projects.

To sync bundle with the original repo, do the following::

    export troy_ext_dir=`pwd`
    cd /tmp/
    git clone git@bitbucket.org:shantenujha/aimes.git
    cd aimes
    git checkout troy_devel
    cp -R modules/bundle/ $troy_ext_dir/
    rm -rf /tmp/aimes
    cd $troy_ext_dir
    git add bundle
    git commit -am 'update bundle from aimes repo'

The thus copied code in external/bundle should never be changed (unless you
really know how to create local patches, i.e. you know what you are doing) --
instead all changes to the bundle module should happen in the `troy_devel`
branch of the `aimes` repository -- as Matteo or Shantenu for access.


