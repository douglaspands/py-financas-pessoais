if __name__ == "__main__":
    from app.infra import create_cli

    app = create_cli()
    app()

else:
    from app.infra import create_asgi

    app = create_asgi()

__all__ = ["app"]
