import subprocess


class GitAgent:

    def sync(self, message: str):

        commands = [
            ["git", "add", "."],
            ["git", "commit", "-m", message],
        ]

        for command in commands:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

            if result.stdout:
                print(result.stdout.strip())

            if result.stderr:
                print(result.stderr.strip())

        print("✅ Git-Änderungen lokal gespeichert")