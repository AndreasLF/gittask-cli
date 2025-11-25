import typer
from ..config import ConfigManager
import questionary

app = typer.Typer()

@app.command()
def login():
    """
    Authenticate with Asana.
    """
    token = questionary.password("Enter your Asana Personal Access Token:").ask()
    if token:
        config = ConfigManager()
        config.set_api_token(token)
        typer.echo("✅ Token saved securely.")
    else:
        typer.echo("❌ No token provided.")

@app.command()
def logout():
    """
    Remove the stored Asana token.
    """
    config = ConfigManager()
    config.set_api_token("") # Keyring doesn't easily support delete in all backends, setting to empty is safer
    typer.echo("✅ Token removed.")
