def generate_ai_fix(issue, code):

    if "password" in issue.lower():
        return "Avoid hardcoding passwords. Use environment variables like: process.env.DB_PASSWORD"

    elif "http" in issue.lower():
        return "Use HTTPS instead of HTTP to encrypt network communication."

    elif "debug" in issue.lower():
        return "Remove console.log statements before committing production code."

    elif "eval" in issue.lower():
        return "Avoid eval() because it can execute malicious code. Use safer parsing methods."

    else:
        return "Follow secure coding best practices."