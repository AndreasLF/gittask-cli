import asana
from typing import Optional, List, Dict
import datetime

class AsanaClient:
    def __init__(self, personal_access_token: str):
        configuration = asana.Configuration()
        configuration.access_token = personal_access_token
        self.api_client = asana.ApiClient(configuration)
        
        self.users_api = asana.UsersApi(self.api_client)
        self.tasks_api = asana.TasksApi(self.api_client)
        self.stories_api = asana.StoriesApi(self.api_client)
        self.workspaces_api = asana.WorkspacesApi(self.api_client)
        self.projects_api = asana.ProjectsApi(self.api_client)
        self.tags_api = asana.TagsApi(self.api_client)
        self.custom_fields_api = asana.CustomFieldsApi(self.api_client)
        self.time_tracking_api = asana.TimeTrackingEntriesApi(self.api_client)
        self.typeahead_api = asana.TypeaheadApi(self.api_client)
        
        # Get current user
        # v5 returns a dict directly
        self.me = self.users_api.get_user("me", opts={})

    def close(self):
        if hasattr(self.api_client, 'pool') and self.api_client.pool:
            self.api_client.pool.close()
            self.api_client.pool.join()
            del self.api_client.pool

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_user_gid(self) -> str:
        return self.me['gid']

    def search_tasks(self, workspace_gid: str, query: str) -> List[Dict]:
        """
        Search for tasks in a workspace using Typeahead.
        """
        opts = {
            "query": query,
            "opt_fields": "name,gid,completed"
        }
        result = self.typeahead_api.typeahead_for_workspace(
            workspace_gid,
            "task",
            opts
        )
        # Result is a generator, convert to list
        return list(result)

    def create_task(self, workspace_gid: str, project_gid: Optional[str], name: str) -> Dict:
        data = {
            "workspace": workspace_gid,
            "name": name,
            "assignee": self.me['gid']
        }
        if project_gid:
            data["projects"] = [project_gid]
            
        body = {"data": data}
        result = self.tasks_api.create_task(body, opts={})
        return result

    def log_time_comment(self, task_gid: str, duration_seconds: float, branch_name: str):
        """
        Log time as a comment on the task.
        """
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        
        time_str = []
        if hours > 0:
            time_str.append(f"{hours}h")
        if minutes > 0:
            time_str.append(f"{minutes}m")
            
        if not time_str:
            time_str.append("&lt; 1m")
            
        text = f"⏱️ Worked {' '.join(time_str)} on branch <code>{branch_name}</code>."
        self.post_comment(task_gid, text)

    def post_comment(self, task_gid: str, text: str):
        """
        Post a comment to a task.
        """
        
        if not text.startswith("<body>"):
            text = f"<body>{text}\n🤖 created with <a href='https://github.com/AndreasLF/gittask'>gittask cli tool</a></body>"
        else:
            text = text.replace("</body>", f"\n🤖 created with <a href='https://github.com/AndreasLF/gittask'>gittask cli tool</a></body>")
            
        body = {"data": {"html_text": text}}
        self.stories_api.create_story_for_task(body, task_gid, opts={})

    def complete_task(self, task_gid: str):
        """
        Mark a task as completed.
        """
        body = {"data": {"completed": True}}
        self.tasks_api.update_task(body, task_gid, opts={})

    def get_workspaces(self) -> List[Dict]:
        result = self.workspaces_api.get_workspaces(opts={})
        return list(result)

    def get_workspace_by_gid(self, workspace_gid: str) -> Dict:
        result = self.workspaces_api.get_workspace(workspace_gid, opts={})
        return result

    def get_projects(self, workspace_gid: str) -> List[Dict]:
        result = self.projects_api.get_projects_for_workspace(workspace_gid, opts={})
        return list(result)

    def get_tags(self, workspace_gid: str) -> List[Dict]:
        """
        Get all tags in the workspace.
        """
        result = self.tags_api.get_tags_for_workspace(workspace_gid, opts={'opt_fields': 'name,gid'})
        return list(result)

    def create_tag(self, workspace_gid: str, name: str, color: Optional[str] = None) -> Dict:
        """
        Create a new tag.
        """
        data = {"workspace": workspace_gid, "name": name}
        if color:
            data["color"] = color
            
        body = {"data": data}
        result = self.tags_api.create_tag(body, opts={})
        return result

    def add_tag_to_task(self, task_gid: str, tag_gid: str):
        """
        Add a tag to a task.
        """
        body = {"data": {"tag": tag_gid}}
        self.tasks_api.add_tag_for_task(body, task_gid)

    def get_project_tasks(self, project_gid: str) -> List[Dict]:
        """
        Get all open tasks in a project.
        """
        opts = {
            'project': project_gid,
            'completed_since': 'now',  # Only incomplete tasks
            'opt_fields': 'name,gid,completed'
        }
        result = self.tasks_api.get_tasks(opts=opts)
        return list(result)

    def assign_task(self, task_gid: str, assignee_gid: str):
        """
        Assign a task to a user.
        """
        body = {"data": {"assignee": assignee_gid}}
        self.tasks_api.update_task(body, task_gid, opts={})

    def get_custom_fields(self, workspace_gid: str) -> List[Dict]:
        """
        Get all custom fields in the workspace.
        """
        result = self.custom_fields_api.get_custom_fields_for_workspace(workspace_gid, opts={'opt_fields': 'name,gid,type,enum_options'})
        return list(result)

    def get_task_with_fields(self, task_gid: str) -> Dict:
        """
        Get a task with all its custom fields.
        """
        opts = {'opt_fields': 'name,custom_fields.name,custom_fields.gid,custom_fields.type,custom_fields.display_value,custom_fields.number_value,actual_time_minutes'}
        return self.tasks_api.get_task(task_gid, opts=opts)

    def get_actual_time(self, task_gid: str) -> Optional[float]:
        """
        Get the actual time in minutes for a task.
        """
        task = self.tasks_api.get_task(task_gid, opts={'opt_fields': 'actual_time_minutes'})
        return task.get('actual_time_minutes')

    def add_time_entry(self, task_gid: str, duration_seconds: int, entered_on: Optional[datetime.date] = None):
        """
        Add a time tracking entry to a task.
        """
        if entered_on is None:
            entered_on = datetime.date.today()
        duration_minutes = int(duration_seconds // 60)
        if duration_minutes == 0:
            # round up to one minute
            duration_minutes = 1

        data = {
            "duration_minutes": duration_minutes,
            "entered_on": entered_on.isoformat()
        }
        body = {"data": data}
        self.time_tracking_api.create_time_tracking_entry(body, task_gid, opts={})
