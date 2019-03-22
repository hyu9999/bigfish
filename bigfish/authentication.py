from rest_framework.authentication import SessionAuthentication


class CrsfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # Do not perform CSRF check
        return
