from django.contrib.auth.mixins import UserPassesTestMixin


class ChefOrAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_chef or self.request.user.is_admin
        )


class WaiterOrAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_waiter or self.request.user.is_admin
        )


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin
