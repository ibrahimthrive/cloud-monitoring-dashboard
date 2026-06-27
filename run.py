"""Development entrypoint. Production uses gunicorn (see Dockerfile)."""
import os

from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    # use_reloader=False: the reloader's second process re-runs db.create_all()
    # on startup, which collides with OneDrive's file lock on instance/monitoring.db
    # and raises "unable to open database file" when this project lives in a
    # OneDrive-synced folder.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), use_reloader=False)
