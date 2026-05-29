if __name__ == "__main__":
    from app.infra.cli import create_app

    app = create_app()
    app()

else:
    from app.infra.asgi import create_app

    app = create_app()

__all__ = ["app"]
