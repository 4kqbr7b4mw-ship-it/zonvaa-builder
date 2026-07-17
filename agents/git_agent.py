import subprocess


class GitAgent:

    def sync(self, message: str):

        commands = [
            ["git", "add", "."],
            ["git", "commit", "-m", message],
            ["git", "push"],
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

            if result.returncode != 0 and command[:2] != ["git", "commit"]:
                raise RuntimeError(
                    f"Git-Befehl fehlgeschlagen: {' '.join(command)}"
                )

        print("✅ GitHub synchronisiert")