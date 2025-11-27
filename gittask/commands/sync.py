import typer
from ..database import DBManager
from ..config import ConfigManager
from ..asana_client import AsanaClient
from rich.console import Console
from rich.progress import track

console = Console()

def sync():
    """
    Sync local time sessions to Asana.
    """
    db = DBManager()
    config = ConfigManager()
    token = config.get_api_token()
    
    if not token:
        console.print("[red]Not authenticated.[/red]")
        raise typer.Exit(code=1)
        
    with AsanaClient(token) as client:
        unsynced = db.get_unsynced_sessions()
        
        if not unsynced:
            console.print("[green]Nothing to sync.[/green]")
            return

        # Filter out open sessions (end_time is None)
        sessions_to_sync = [s for s in unsynced if s['end_time'] is not None]
        
        if not sessions_to_sync:
            console.print("[yellow]Only active sessions found. Stop them to sync.[/yellow]")
            return

        console.print(f"Syncing {len(sessions_to_sync)} sessions...")
        
        for session in track(sessions_to_sync, description="Syncing..."):
            try:
                if config.get_paid_plan_status():
                    # Only possible to log time on paid plans
                    client.add_time_entry(
                        session['task_gid'],
                        session['duration_seconds']
                    )
                else: 
                    client.log_time_comment(
                        session['task_gid'],
                        session['duration_seconds'],
                        session['branch']
                    )
                db.mark_session_synced(session['id'])
            except Exception as e:
                console.print(f"[red]Failed to sync session {session['id']}: {e}[/red]")
            
    console.print("[bold green]Sync complete![/bold green]")
