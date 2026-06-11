import time
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

SECRET_PASSWORD = "519265"
SECRET_USERNAME = "admin"

# Delay per correct prefix character (seconds).
# Large enough to measure reliably on a local machine.
DELAY_PER_CHAR = 0.002


def _vulnerable_check(username: str, password: str) -> bool:
    """
    Intentionally vulnerable password check.
    Iterates character by character and sleeps on each match,
    leaking how many leading characters of the guess are correct.
    """
    if username != SECRET_USERNAME:
        return False

    for i, ch in enumerate(password):
        if i >= len(SECRET_PASSWORD) or ch != SECRET_PASSWORD[i]:
            return False
        time.sleep(DELAY_PER_CHAR)

    return len(password) == len(SECRET_PASSWORD)


def safe_check(username: str, password: str) -> bool:
    """
    stub for safe password check
    To be completed by you!
    """
    if username != SECRET_USERNAME:
        return False

    result = True

    for i, ch in enumerate(password):
        # i == index of the current character
        # ch == current character
        
        # code below is vulnerable. Fix it!
        # then replace _vulnerable_check with safe_check in login_view() below
        if i >= len(SECRET_PASSWORD) or ch != SECRET_PASSWORD[i]:
            return False
        time.sleep(DELAY_PER_CHAR)

    return len(password) == len(SECRET_PASSWORD)

def safe_check2(username: str, password: str) -> bool:
    """
    Constant-time password check.
    Iterates through the entire string and uses bitwise operations 
    to prevent short-circuiting, eliminating the timing side-channel.
    """
    if username != SECRET_USERNAME:
        return False

    # If the lengths don't match, we can immediately reject it.
    # (Note: While this does leak the *length* of the password, the 
    # assignment's primary goal is protecting the character contents).
    if len(password) != len(SECRET_PASSWORD):
        return False

    result = 0

    for i in range(len(SECRET_PASSWORD)):
        # 1. Convert characters to their integer Unicode values using ord()
        # 2. XOR (^) the values. If they match, XOR outputs 0. If they differ, it outputs > 0.
        # 3. Bitwise OR (|) accumulates any differences into the 'result' variable.
        result |= ord(password[i]) ^ ord(SECRET_PASSWORD[i])
        
        # We execute the sleep function on EVERY iteration, regardless of a match.
        time.sleep(DELAY_PER_CHAR)

    # If result is still 0, no differences were found.
    return result == 0






@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        t0 = time.perf_counter()
        success = _vulnerable_check(username, password) # replace with safe_check as neede!
        elapsed_ms = (time.perf_counter() - t0) * 1000

        if success:
            return render(request, "login/login.html", {
                "success": True,
                "elapsed_ms": f"{elapsed_ms:.1f}",
            })
        return render(request, "login/login.html", {
            "error": "Invalid credentials.",
            "elapsed_ms": f"{elapsed_ms:.1f}",
            "guess": password,
        })

    return render(request, "login/login.html")
