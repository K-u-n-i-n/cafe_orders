from django.contrib.auth.mixins import UserPassesTestMixin


class ChefRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_chef


class WaiterRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_waiter
