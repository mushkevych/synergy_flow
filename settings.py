# module is required to initialized synergy.conf and run unit tests

settings = dict(
    log_directory='/var/log/synergy-flow',
    debug=True,                # if True, logger.setLevel is set to DEBUG. Otherwise to INFO

    under_test=True            # marks execution of the Unit Tests
                               # if True, a console handler for STDOUT and STDERR are appended to the logger.
                               # Otherwise STDOUT and STDERR are redirected to .log files
)

# Update current dict with the environment-specific settings
try:
    overrides = __import__('settings_secrets')
    settings.update(overrides.settings)
except:
    pass
