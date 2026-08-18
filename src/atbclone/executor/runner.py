"""Shell script executor with standard and admin elevation support."""

import subprocess


class CloneError(Exception):
    """Raised when an executor command fails."""

    pass


class Runner:
    """Executes shell scripts directly or with administrator privileges."""

    @staticmethod
    def run(script: str, needs_admin: bool = False) -> str:
        """Execute a shell script directly or via osascript with admin elevation.

        Args:
            script: The shell command or script to execute.
            needs_admin: If True, execute via osascript with administrator privileges.

        Returns:
            The standard output (and standard error) of the execution as a string.

        Raises:
            CloneError: If the script fails or returns a non-zero exit code.
        """
        if needs_admin:
            return Runner._run_as_admin(script)
        else:
            return Runner._run_direct(script)

    @staticmethod
    def _run_direct(script: str) -> str:
        """Run script directly via subprocess in a shell."""
        try:
            return subprocess.check_output(
                script, shell=True, stderr=subprocess.STDOUT, text=True
            )
        except subprocess.CalledProcessError as e:
            raise CloneError(f"Command failed (exit {e.returncode}):\n{e.output}") from e

    @staticmethod
    def _run_as_admin(script: str) -> str:
        """Run script using AppleScript osascript with administrator privileges."""
        escaped = script.replace("\\", "\\\\").replace('"', '\\"')
        applescript = f'do shell script "{escaped}" with administrator privileges'
        try:
            return subprocess.check_output(
                ["/usr/bin/osascript", "-e", applescript],
                stderr=subprocess.STDOUT,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise CloneError(f"Admin command failed:\n{e.output}") from e
