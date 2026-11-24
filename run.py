from dotenv import load_dotenv

load_dotenv()  # reads .env if present; real environment variables still win

from app import create_app  # noqa: E402  (must come after load_dotenv)

app = create_app()

if __name__ == "__main__":
    cfg = app.extensions["config"]
    app.run(host=cfg.HOST, port=cfg.PORT, debug=cfg.DEBUG)
