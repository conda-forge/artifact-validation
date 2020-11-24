# do not clobber yamls

This directory holds YAML files specifying paths that cannot be clobbered
except by artifacts on an allowed list.

The format is

```yaml
# the glob(s) to check relative to the PREFIX
files:
  # it may not be a glob at all
  - "bin/conda"
  # if it is a directory, everything in the directory is included recursively
  - "lib/python*/site-packages/conda"
  # you can use ** too to match none or more subdirs
  - "lib/**/*.so"

# list of packages allowed to write the files above
allowed:
  - conda
```
