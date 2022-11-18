class FieldPatch:
    def __init__(self, min_build, max_build, patch):
        self.min_build = min_build
        self.max_build = max_build
        self.patch = patch

    def should_apply(self, build):
        if self.min_build == 0 and self.max_build == 0:
            return True

        return (build >= self.min_build) and (build <= self.max_build)
