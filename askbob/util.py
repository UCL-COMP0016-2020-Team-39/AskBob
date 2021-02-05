

def setup_logging():
    import logging
    import coloredlogs

    coloredlogs.install(
        level=logging.INFO,
        use_chroot=False,
        fmt="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s"
    )
