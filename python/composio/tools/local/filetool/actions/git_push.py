import datetime
import os
import typing as t
import uuid
from pathlib import Path

from pydantic import Field

from composio.tools.base.local import LocalAction
from composio.tools.local.filetool.actions.base_action import (
    BaseFileRequest,
    BaseFileResponse,
    include_cwd,
)


class GitPushRequest(BaseFileRequest):
    """Request to create a new branch and push to origin."""

    new_file_paths: t.List[str] = Field(
        default=[],
        description="Paths of the files newly created to be included in the commit.",
    )
    branch_name: t.Optional[str] = Field(
        None,
        description="Name of the new branch to create and push. If not provided, a unique name will be generated.",
    )


class GitPushResponse(BaseFileResponse):
    """Response to creating a new branch and pushing to origin."""

    success: bool = Field(False, description="Whether the push was successful")
    message: str = Field("", description="Status message or error description")
    branch_name: str = Field(
        "", description="The name of the branch that was created and pushed"
    )


class GitPush(LocalAction[GitPushRequest, GitPushResponse]):
    """
    Create a new branch, add changes, and push to origin.

    This action creates a new branch with the specified name (or generates a unique name if not provided),
    adds all changes (including new files), commits the changes, and pushes the new branch to origin.

    Usage example:
    new_file_paths: ["path/to/new/file1.txt", "path/to/new/file2.py"]
    branch_name: "feature/new-awesome-feature"  # Optional

    Note: This action should be run after all changes are made to add, commit, and push the result.
    """

    display_name = "Create Branch and Push to Origin"
    _request_schema = GitPushRequest
    _response_schema = GitPushResponse

    @include_cwd  # type: ignore
    def execute(self, request: GitPushRequest, metadata: t.Dict) -> GitPushResponse:
        file_manager = self.filemanagers.get(request.file_manager_id)
        git_root = self._find_git_root(file_manager.current_dir())
        if not git_root:
            return GitPushResponse(
                success=False,
                message="Not in a git repository or its subdirectories",
                branch_name="",
            )

        original_dir = file_manager.current_dir()
        file_manager.chdir(str(git_root))

        try:
            # Generate a unique branch name if not provided
            branch_name = request.branch_name or self._generate_branch_name()

            # Create new branch
            _, error = file_manager.execute_command(f"git checkout -b {branch_name}")
            if error:
                raise RuntimeError(f"Error creating new branch: {error}")

            # Add new files if specified
            if request.new_file_paths:
                for file_path in request.new_file_paths:
                    _, error = file_manager.execute_command(f"git add {file_path}")
                    if error:
                        raise RuntimeError(f"Error adding new file: {error}")

            # Stage all changes
            _, error = file_manager.execute_command("git add -A")
            if error:
                raise RuntimeError(f"Error staging changes: {error}")

            # Set up Git configuration using environment variables
            github_access_token = os.environ.get("GITHUB_ACCESS_TOKEN", "").strip()
            if not github_access_token:
                raise RuntimeError("GitHub access token not found in environment variables")

            # Set Git config for this repository
            _, error = file_manager.execute_command('git config user.name "GitHub Actions"')
            if error:
                raise RuntimeError(f"Error setting Git user name: {error}")

            _, error = file_manager.execute_command('git config user.email "actions@github.com"')
            if error:
                raise RuntimeError(f"Error setting Git user email: {error}")

            # Commit changes
            _, error = file_manager.execute_command(
                f'git commit -m "Initial commit for {branch_name}"'
            )
            if error:
                raise RuntimeError(f"Error committing changes: {error}")

            # Push to origin using the GitHub access token
            push_command = f"git -c http.extraheader='Authorization: Bearer {github_access_token}' push -u origin {branch_name}"
            output, error = file_manager.execute_command(push_command)
            
            if error:
                raise RuntimeError(f"Error pushing to origin: {error}")

            return GitPushResponse(
                success=True,
                message=f"Successfully created and pushed branch '{branch_name}' to origin",
                branch_name=branch_name,
            )

        except Exception as e:
            return GitPushResponse(success=False, message=str(e), branch_name="")

        finally:
            file_manager.chdir(original_dir)

    def _find_git_root(self, path: str) -> t.Optional[Path]:
        """Find the root of the git repository."""
        current = Path(path).resolve()
        while current != current.parent:
            if (current / ".git").is_dir():
                return current
            current = current.parent
        return None

    def _generate_branch_name(self) -> str:
        """Generate a unique branch name."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"auto-branch-{timestamp}-{unique_id}"
