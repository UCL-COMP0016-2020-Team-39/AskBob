def setup_logging():
    import logging
    import coloredlogs
    import os

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

    coloredlogs.install(
        level=logging.INFO,
        use_chroot=False,
        fmt="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s"
    )
