class LoginPage:
    """Everything the tests need to know about the DineFlash login screen.
    If the site changes, you only fix the locators here."""

    def __init__(self, page, url):
        self.page = page
        self.url = url
        # Locators (how Playwright finds things on the page)
        self.username = page.locator("input[type='text'], input[name*='user' i]").first
        self.password = page.locator("input[type='password']").first
        self.sign_in = page.get_by_role("button", name="Sign In")
        self.forgot_password = page.get_by_text("Forgot Password?")
        # The site shows its errors as browser pop-ups (alert). Record and close them.
        self.dialogs = []
        page.on("dialog", self._on_dialog)

    def _on_dialog(self, dialog):
        self.dialogs.append(dialog.message)
        with open("popup_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{self.page.url} | {dialog.message}\n")
        dialog.dismiss()

    def open(self):
        self.page.goto(self.url)
        self.sign_in.wait_for()
        # The page runs background scripts on load; signing in before they finish is ignored.
        self.page.wait_for_timeout(2500)

    def login(self, user, pwd):
        self.username.fill(user)
        self.password.fill(pwd)
        self.page.wait_for_timeout(1000)
        self.sign_in.click()
        # A successful login leaves /login/; a failed one stays, so wait briefly for the move.
        try:
            self.page.wait_for_url(lambda u: "/login" not in u, timeout=6000)
        except Exception:
            pass
        # Occasionally the click is ignored (BUG-02). If nothing happened at all, retry once.
        if self.is_on_login_page() and not self.dialogs and user and pwd:
            self.page.wait_for_timeout(1500)
            if self.username.input_value() == user:
                self.sign_in.click()
                try:
                    self.page.wait_for_url(lambda u: "/login" not in u, timeout=6000)
                except Exception:
                    pass
        self.settle()

    def is_on_login_page(self):
        return "/login" in self.page.url


    def settle(self):
        """Wait for the page to react after Sign In.
        (networkidle never finishes on this site, so we wait for 'load' plus a short pause.)"""
        try:
            self.page.wait_for_load_state("load", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(2000)


